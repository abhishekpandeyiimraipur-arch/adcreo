#!/bin/bash
# scripts/broll_output/trim_commands.sh
# Trim + crop each picked clip to 3000ms, 1080Ã—1920.
# Run from: backend root
# Prereq: ffmpeg installed
# REVIEW trim_start_ms per clip â€” default is 0 (start of file).
# Adjust -ss value (seconds) if the best 3s of the clip starts later.
set -e

# â”€â”€ d2c_beauty__hook_1  (pexels_16478020) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_d2c_beauty_hook_1.mp4 "https://videos.pexels.com/video-files/16478020/16478020-hd_1920_1080_24fps.mp4"
ffmpeg -i /tmp/adcreo_broll_d2c_beauty_hook_1.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/d2c_beauty__hook_1.mp4
rm -f /tmp/adcreo_broll_d2c_beauty_hook_1.mp4
echo "âœ“ scripts/broll_output/final_clips/d2c_beauty__hook_1.mp4"

# â”€â”€ d2c_beauty__hook_2  (pexels_10532909) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_d2c_beauty_hook_2.mp4 "https://videos.pexels.com/video-files/10532909/10532909-hd_1080_2048_25fps.mp4"
ffmpeg -i /tmp/adcreo_broll_d2c_beauty_hook_2.mp4 \
  -ss 0 -t 3.0 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/d2c_beauty__hook_2.mp4
rm -f /tmp/adcreo_broll_d2c_beauty_hook_2.mp4
echo "âœ“ scripts/broll_output/final_clips/d2c_beauty__hook_2.mp4"

# â”€â”€ d2c_beauty__context  (pexels_20349690) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_d2c_beauty_context.mp4 "https://videos.pexels.com/video-files/20349690/20349690-hd_1920_1080_60fps.mp4"
ffmpeg -i /tmp/adcreo_broll_d2c_beauty_context.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/d2c_beauty__context_1.mp4
rm -f /tmp/adcreo_broll_d2c_beauty_context.mp4
echo "âœ“ scripts/broll_output/final_clips/d2c_beauty__context_1.mp4"

# â”€â”€ d2c_beauty__cta_bg  (pexels_8516623) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_d2c_beauty_cta_bg.mp4 "https://videos.pexels.com/video-files/8516623/8516623-hd_1080_1920_30fps.mp4"
ffmpeg -i /tmp/adcreo_broll_d2c_beauty_cta_bg.mp4 \
  -ss 0 -t 3.0 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/d2c_beauty__cta_bg_1.mp4
rm -f /tmp/adcreo_broll_d2c_beauty_cta_bg.mp4
echo "âœ“ scripts/broll_output/final_clips/d2c_beauty__cta_bg_1.mp4"

# â”€â”€ packaged_food__hook_1  (pexels_8597293) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_packaged_food_hook_1.mp4 "https://videos.pexels.com/video-files/8597293/8597293-hd_1920_1080_30fps.mp4"
ffmpeg -i /tmp/adcreo_broll_packaged_food_hook_1.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/packaged_food__hook_1.mp4
rm -f /tmp/adcreo_broll_packaged_food_hook_1.mp4
echo "âœ“ scripts/broll_output/final_clips/packaged_food__hook_1.mp4"

# â”€â”€ packaged_food__context  (pexels_10071214) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_packaged_food_context.mp4 "https://videos.pexels.com/video-files/10071214/10071214-hd_1080_2048_25fps.mp4"
ffmpeg -i /tmp/adcreo_broll_packaged_food_context.mp4 \
  -ss 0 -t 3.0 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/packaged_food__context_1.mp4
rm -f /tmp/adcreo_broll_packaged_food_context.mp4
echo "âœ“ scripts/broll_output/final_clips/packaged_food__context_1.mp4"

# â”€â”€ packaged_food__cta_bg  (pexels_7045895) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_packaged_food_cta_bg.mp4 "https://videos.pexels.com/video-files/7045895/7045895-hd_1366_658_30fps.mp4"
ffmpeg -i /tmp/adcreo_broll_packaged_food_cta_bg.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/packaged_food__cta_bg_1.mp4
rm -f /tmp/adcreo_broll_packaged_food_cta_bg.mp4
echo "âœ“ scripts/broll_output/final_clips/packaged_food__cta_bg_1.mp4"

# â”€â”€ electronics__hook_1  (pexels_3712700) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_electronics_hook_1.mp4 "https://videos.pexels.com/video-files/3712700/3712700-hd_1080_2048_25fps.mp4"
ffmpeg -i /tmp/adcreo_broll_electronics_hook_1.mp4 \
  -ss 0 -t 3.0 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/electronics__hook_1.mp4
rm -f /tmp/adcreo_broll_electronics_hook_1.mp4
echo "âœ“ scripts/broll_output/final_clips/electronics__hook_1.mp4"

# â”€â”€ electronics__hook_2  (pexels_14209120) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_electronics_hook_2.mp4 "https://videos.pexels.com/video-files/14209120/14209120-hd_1920_1080_30fps.mp4"
ffmpeg -i /tmp/adcreo_broll_electronics_hook_2.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/electronics__hook_2.mp4
rm -f /tmp/adcreo_broll_electronics_hook_2.mp4
echo "âœ“ scripts/broll_output/final_clips/electronics__hook_2.mp4"

# â”€â”€ electronics__context  (pexels_12257306) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_electronics_context.mp4 "https://videos.pexels.com/video-files/12257306/12257306-hd_1280_720_60fps.mp4"
ffmpeg -i /tmp/adcreo_broll_electronics_context.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/electronics__context_1.mp4
rm -f /tmp/adcreo_broll_electronics_context.mp4
echo "âœ“ scripts/broll_output/final_clips/electronics__context_1.mp4"

# â”€â”€ electronics__cta_bg  (pexels_3755074) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_electronics_cta_bg.mp4 "https://videos.pexels.com/video-files/3755074/3755074-hd_1080_2048_25fps.mp4"
ffmpeg -i /tmp/adcreo_broll_electronics_cta_bg.mp4 \
  -ss 0 -t 3.0 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/electronics__cta_bg_1.mp4
rm -f /tmp/adcreo_broll_electronics_cta_bg.mp4
echo "âœ“ scripts/broll_output/final_clips/electronics__cta_bg_1.mp4"

# â”€â”€ hard_accessories__hook_1  (pexels_7829858) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_hard_accessories_hook_1.mp4 "https://videos.pexels.com/video-files/7829858/7829858-hd_1920_1080_30fps.mp4"
ffmpeg -i /tmp/adcreo_broll_hard_accessories_hook_1.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/hard_accessories__hook_1.mp4
rm -f /tmp/adcreo_broll_hard_accessories_hook_1.mp4
echo "âœ“ scripts/broll_output/final_clips/hard_accessories__hook_1.mp4"

# â”€â”€ hard_accessories__hook_2  (pexels_5678004) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_hard_accessories_hook_2.mp4 "https://videos.pexels.com/video-files/5678004/5678004-hd_2048_1080_30fps.mp4"
ffmpeg -i /tmp/adcreo_broll_hard_accessories_hook_2.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/hard_accessories__hook_2.mp4
rm -f /tmp/adcreo_broll_hard_accessories_hook_2.mp4
echo "âœ“ scripts/broll_output/final_clips/hard_accessories__hook_2.mp4"

# â”€â”€ hard_accessories__context  (pexels_6278961) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_hard_accessories_context.mp4 "https://videos.pexels.com/video-files/6278961/6278961-hd_2048_1080_25fps.mp4"
ffmpeg -i /tmp/adcreo_broll_hard_accessories_context.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/hard_accessories__context_1.mp4
rm -f /tmp/adcreo_broll_hard_accessories_context.mp4
echo "âœ“ scripts/broll_output/final_clips/hard_accessories__context_1.mp4"

# â”€â”€ hard_accessories__cta_bg  (pexels_9603572) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_hard_accessories_cta_bg.mp4 "https://videos.pexels.com/video-files/9603572/9603572-hd_2048_1080_25fps.mp4"
ffmpeg -i /tmp/adcreo_broll_hard_accessories_cta_bg.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/hard_accessories__cta_bg_1.mp4
rm -f /tmp/adcreo_broll_hard_accessories_cta_bg.mp4
echo "âœ“ scripts/broll_output/final_clips/hard_accessories__cta_bg_1.mp4"

# â”€â”€ home_kitchen__hook_2  (pexels_7830747) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_home_kitchen_hook_2.mp4 "https://videos.pexels.com/video-files/7830747/7830747-hd_1920_1080_30fps.mp4"
ffmpeg -i /tmp/adcreo_broll_home_kitchen_hook_2.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/home_kitchen__hook_2.mp4
rm -f /tmp/adcreo_broll_home_kitchen_hook_2.mp4
echo "âœ“ scripts/broll_output/final_clips/home_kitchen__hook_2.mp4"

# â”€â”€ home_kitchen__context  (pexels_6278959) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_home_kitchen_context.mp4 "https://videos.pexels.com/video-files/6278959/6278959-hd_2048_1080_25fps.mp4"
ffmpeg -i /tmp/adcreo_broll_home_kitchen_context.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/home_kitchen__context_1.mp4
rm -f /tmp/adcreo_broll_home_kitchen_context.mp4
echo "âœ“ scripts/broll_output/final_clips/home_kitchen__context_1.mp4"

# â”€â”€ home_kitchen__cta_bg  (pexels_20349691) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_home_kitchen_cta_bg.mp4 "https://videos.pexels.com/video-files/20349691/20349691-hd_720_1280_60fps.mp4"
ffmpeg -i /tmp/adcreo_broll_home_kitchen_cta_bg.mp4 \
  -ss 0 -t 3.0 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/home_kitchen__cta_bg_1.mp4
rm -f /tmp/adcreo_broll_home_kitchen_cta_bg.mp4
echo "âœ“ scripts/broll_output/final_clips/home_kitchen__cta_bg_1.mp4"

# â”€â”€ d2c_fashion__hook_1  (pexels_7233560) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_d2c_fashion_hook_1.mp4 "https://videos.pexels.com/video-files/7233560/7233560-hd_1920_1080_30fps.mp4"
ffmpeg -i /tmp/adcreo_broll_d2c_fashion_hook_1.mp4 \
  -ss 0 -t 3.0 \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/d2c_fashion__hook_1.mp4
rm -f /tmp/adcreo_broll_d2c_fashion_hook_1.mp4
echo "âœ“ scripts/broll_output/final_clips/d2c_fashion__hook_1.mp4"

# â”€â”€ d2c_fashion__context  (pexels_8102655) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_d2c_fashion_context.mp4 "https://videos.pexels.com/video-files/8102655/8102655-hd_1080_2048_25fps.mp4"
ffmpeg -i /tmp/adcreo_broll_d2c_fashion_context.mp4 \
  -ss 0 -t 3.0 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/d2c_fashion__context_1.mp4
rm -f /tmp/adcreo_broll_d2c_fashion_context.mp4
echo "âœ“ scripts/broll_output/final_clips/d2c_fashion__context_1.mp4"

# â”€â”€ d2c_fashion__cta_bg  (pexels_10527009) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
curl -L -o /tmp/adcreo_broll_d2c_fashion_cta_bg.mp4 "https://videos.pexels.com/video-files/10527009/10527009-hd_1080_2048_25fps.mp4"
ffmpeg -i /tmp/adcreo_broll_d2c_fashion_cta_bg.mp4 \
  -ss 0 -t 3.0 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -crf 18 -an \
  scripts/broll_output/final_clips/d2c_fashion__cta_bg_1.mp4
rm -f /tmp/adcreo_broll_d2c_fashion_cta_bg.mp4
echo "âœ“ scripts/broll_output/final_clips/d2c_fashion__cta_bg_1.mp4"
