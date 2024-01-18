The site resides at [heroku](https://hello-internet-c2d83d7d2d7e.herokuapp.com/captchapractice/). It might take a second to wake up.

### Purpose of this Project

The goal of this project is *not* to build a 1-to-1 clone of Google's reCaptcha since its scope is incredibly large. Rather, we aim to mimic the experience when solving various "Are you human?" challenges found across the internet. 

This (as of Jan '24) is still a work-in-progress and is not the final product envisioned. Nonetheless, this is a demonstration of my learning; and the complexity of this project will improve as my general experience does. 

### Background

To protect websites from fraud and abuse, websites employ a security measure to distinguish between human users and automated bots. Google's reCAPTCHA v2's base layer is the ***invisible* reCAPTCHA** which automatically analyses a user's actions (mouse movements, keyboard inputs, human-like patterns and signals) to determine if the user is likely human.

If the system is not confident that you are human, it prompts you with additional verification challenges. One type of challenge asks you to "select all images with cars" or  or "Select all images containing street signs" or some variant of this prompt.

### Requirements

1. The superuser can upload images. The app currently handles the formatting and display logic, however, the superuser must manually choose which objects the Captcha tests for. 
2. Users can view a list of captcha (signed in or not).
3. Users can solve any individual captcha or can choose to solve a series of unique ones (signed in to ensure the same captcha is not repeated for a given account).


### Detailed Design

##### 1. Uploading Captcha
Superusers and admins, through Django's admin interface can contribute their own images for captcha. The admin site is very modular. Thus both the structure and functioning of the admin site has been altered: on Captcha creation, the image is automatically validated and a specified number related models (the *ImageSlice* model which represents a single image of the Captcha grid) using Django's signal dispatcher. The manual, and perhaps tedious, part of this process is selecting which images in the grid display the object the Captcha requires you to select. In the future, I'd like for some type of computer vision to solve this.

##### 2. Users
Users can sign up with a unique username. Django's password validation is turned off to make account creation easier as one's almost expected to try their hand at the captcha multiple times. The responses are saved so that users only view a particular captcha once when trying the 'captcha challenge'. 



### Future Work:
1. Automatically identifying objects and providing an admin the option to choose which image the captcha should evaluate for is a long-term goal.
2. At this moment, only a single *type* of captcha has been implemented. I have two more captcha-types in the pipeline.
3. Provide the option for users to report if a captcha has not been evaluated properly. When paired with Future Work #1, it should help provide feedback on how much of this process can be automated.
4. Speed: I've incorporated asynchronous Javascript to smooth out the experience. However, in production, server response times are slow and image loading is also noticeably slower. I want to explore switching to a geographically closer compute instance (EC2) as well as test if a CDN in front of WhiteNoise will help. 


