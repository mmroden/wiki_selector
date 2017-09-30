# Mass converts a folder of video files to the following spec:
#   15FPS, constant rate factor of 32, backwards compat to all devices (yuv420p)
#   6 reference frames (default recommended), 720:y (scale appropriately),
#   audio is untouched
# In most cases, this shrinks videos well for Pi and mobile use.
import os, subprocess, sys, shutil

inDir  = sys.argv[1]
outDir = sys.argv[2]
ffmpeg = [
    "ffmpeg", 
    "-i", 
    "in.mp4", 
    "-r", 
    "15", 
    "-vcodec", 
    "libx264", 
    "-crf", 
    "32", 
    "-preset", 
    "veryfast", 
    "-profile:v", 
    "baseline",
    "-level", 
    "3", 
    "-refs", 
    "6", 
    "-vf", 
    "scale=720:-2,format=yuv420p",
    "-acodec", 
    "copy", 
    "output.mp4", 
    "-y"
]

# Make input sources user-friendly. Fixes filepaths
if inDir[-1]  != '/': inDir  += '/'
if outDir[-1] != '/': outDir += '/'
# Create output file directory if it doesn't exist
if not os.path.exists(outDir): os.makedirs(outDir)

def main():
  def checkForError(process):
    if process == 1:
      log.write('Could not process: {0}\n'.format(filename))
      print ('====== Could not process: {0}'.format(filename))
      shutil.copy2(inDir + filename, outDir + filename + '.corrupt')
      # with open(outDir + filename + '.corrupt', 'w+') as f:
      #   f.write('Invalid Format')
      #   f.close()
    else:
      print ('converted ' + filename)

  with open('progress.log', 'a') as log:
    for fn in os.listdir(inDir):
      ext = fn.split('.')
      if (ext and len(ext) > 1 and ext[1] == 'mp4'):
        # Update the ffmpeg array (which is actually a command when passed
        # into subprocess) to include to input & output
        filename = ext[0] + '.' +ext[1]
        ffmpeg[2] = inDir + filename
        ffmpeg[-2] = outDir + filename

        # Run ffmpeg with current settings. Then check the return code
        process = subprocess.call(ffmpeg)
        checkForError(process)
    log.close()

if __name__ == "__main__": main()