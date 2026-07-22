import os
import subprocess

def run_test():
    ps_cmd = """
    [void][System.Reflection.Assembly]::LoadWithPartialName("System.Runtime.WindowsRuntime")
    [Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
    [Windows.Storage.Streams.IRandomAccessStream, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
    [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
    [Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType=WindowsRuntime] | Out-Null
    [Windows.Media.Ocr.OcrResult, Windows.Media.Ocr, ContentType=WindowsRuntime] | Out-Null
    
    function Await($op, $type) {
        $asTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { 
            $_.Name -eq 'AsTask' -and 
            $_.GetGenericArguments().Length -eq 1 -and
            $_.GetParameters().Length -eq 1 -and
            $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
        }
        $genericMethod = $asTaskMethod.MakeGenericMethod($type)
        $task = $genericMethod.Invoke($null, @($op))
        return $task.Result
    }
    
    # Create test image with text "HELLO"
    $imgPath = \"""" + os.path.abspath("test.png") + """\"
    
    # Open FileStream natively in .NET
    $fileStream = [System.IO.File]::OpenRead($imgPath)
    
    # Convert .NET Stream to WinRT IRandomAccessStream synchronously!
    $stream = [System.IO.WindowsRuntimeStreamExtensions]::AsRandomAccessStream($fileStream)
    
    # Decode bitmap
    $decoderOp = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)
    $decoder = Await $decoderOp ([Windows.Graphics.Imaging.BitmapDecoder])
    
    $bitmapOp = $decoder.GetSoftwareBitmapAsync()
    $bitmap = Await $bitmapOp ([Windows.Graphics.Imaging.SoftwareBitmap])
    
    # Run OCR
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
    if ($engine -ne $null) {
        $ocrOp = $engine.RecognizeAsync($bitmap)
        $result = Await $ocrOp ([Windows.Media.Ocr.OcrResult])
        Write-Output "OCR_RESULT: $($result.Text)"
    } else {
        Write-Output "ERROR: OCR Engine not available"
    }
    
    # Clean up
    $fileStream.Close()
    """
    
    # Re-generate test image first
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (200, 50), 'white')
    draw = ImageDraw.Draw(img)
    draw.text((10,15), 'HELLO WORLD OCR TEST', fill='black')
    img.save('test.png')
    
    res = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        capture_output=True, text=True, encoding='utf-8', errors='ignore'
    )
    print("STDOUT:", res.stdout.strip())
    print("STDERR:", res.stderr.strip())

run_test()
