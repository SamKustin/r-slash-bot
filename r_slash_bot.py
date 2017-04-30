#!/usr/local/bin/env python

# Sets up tweepy with twitter bot and other important set up info
import tweepy, time, feedparser, re, requests, os
from credentials import *
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# ========================================================================
subreddit = "aww"
url = "http://www.reddit.com/r/" + subreddit

# Get the RSS feed of any url by adding ".rss" to the end of the url
rss_url = url + "/.rss"
feed = feedparser.parse(rss_url)

num_posts = 25

for i in range (num_posts):
    post_title = feed["entries"][i]["title"]
    post_link = feed["entries"][i]["link"]
    tweet_text = post_title + '\n' + post_link

    # Gets html from the post link
    post_content = feed["entries"][i]["content"][0]["value"]
    # Searches for all instances of "href=" in the post_content
    match = re.findall(r'href=[\'"]?([^\'" >]+)', post_content)

    if match:
        # Gets the 3rd href link from the post_content
        # This should be the link to the image/gif
        image_link = match[2]

        # Creates a local temp_file.extension to put the image into
        extension = image_link.split('.')[-1]
        if extension != "gifv":
            image_file = "temp." + extension

            request = requests.get(image_link, stream=True)
            if request.status_code == 200:
                # Downloads the image
                with open(image_file, 'wb') as image:
                    for chunk in request:
                        image.write(chunk)

                # Posts tweet to twitter
                api.update_with_media(image_file, status=tweet_text)
                print("I posted a tweet! Check @CoreProjectBot")

                # Remove local image_file
                os.remove(image_file)

                # Waits 5 minutes before next tweet
                if i != num_posts - 1:
                    time.sleep(60 * 5)

            else:
                print("Error: Cannot download image. Skipping this post.")
        else:
            print("Error: Cannot download gifv file type. Skipping this post.")

# ========================================================================

print("Done! No more reddit posts to tweet.")
