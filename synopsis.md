
# 1) The program scans the folders

# 2) The program decides whether there are new elements that are not on loop ('clips' folder)
     There needs to be a variable "empty time on last clip", which says, how much empty time can be on the end of the video, if we don't extend the time of pictures.
     (clips are based on music. If there is a video that is 0:30 minutes, and a music that is 4:00, there is 3:30 empty time. This time could be filled by reusing components, but if there are new components, this clip should be re-rendered, now with new elements.)

# 3) The already rendered / compiled clips are going to the 'show' RTMP endpoint, with ffmpeg.
     (there is an array of clips)

# 4) NginX is only creating the HLS stream



Where to store data? .txt file, or database?
 (probably first .txt file, later postgres. PostgreSQL is really a little bit overkill)

How to know when we reached end of clip?
 duration is not good enough, there can be lag

nginx can do restream (RTMP)
