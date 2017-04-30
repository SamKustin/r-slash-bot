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

num_posts = 25 # number of posts to tweet
wait_time = 20 # wait 20 minutes between each post

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

        # Gets the extension for the image file
        extension = image_link.split('.')[-1]

        # Changes extensions to gif and jpg
        if extension != "jpg":
            if extension == "gifv":
                extension = "gif"
                print("Error: Cannot download .gifv extension. Changing to .gif extension.")
                # Modify the image link to reflect the change in extension.
                image_link = image_link.replace(image_link.split('.')[-1], extension)
                print("New image_link: " + image_link)
            else:
                extension = "jpg"
                print("Error: Cannot download imgur url. Appending .jpg extension onto imgur url.")
                # Modify the image link to reflect the change in extension.
                # Need for imgur urls: imgur.com/picture -> imgur.com/picture.jpg
                image_link = image_link + ".jpg"
                print("New image_link: " + image_link)

        image_file = "temp." + extension

        # Creates a local temp_file.extension to put the image into
        request = requests.get(image_link, stream=True)
        if request.status_code == 200:
            # Downloads the image
            with open(image_file, 'wb') as image:
                for chunk in request:
                    image.write(chunk)

            # Checks if the image isn't over 3,072,000 bytes (3072 KB)
            file_stats = os.stat(image_file)
            file_size = file_stats.st_size

            if (file_size <= 3072000):
                # Posts tweet to twitter
                api.update_with_media(image_file, status=tweet_text)
                print("I posted a tweet! Check @r_slash_bot")
            else:
                print("Error: image_file is too big (" + str(file_size) + " bytes). Cannot be posted.")

            # Remove local image_file
            os.remove(image_file)

            # Waits 20 minutes before next tweet
            if i != num_posts - 1:
                time.sleep(60 * wait_time)

# ========================================================================

print("Done! No more reddit posts to tweet.")
