The site resides at [render](https://hellointernet.onrender.com/captchapractice/). It will take upto 30 seconds to wake up since Render spins down any of its websites that goes 15 minutes without receiving inbound traffic.

### Project Purpose

The objective of this project is *not* to create an exact replica of Google's reCaptcha due to its extensive scope. Instead, my aim is to simulate the user experience encountered when solving various "Are you human?" challenges commonly found on the internet.

As of March 2024, this project is still a work in progress and does not represent the final envisioned product. Nevertheless, it serves as a demonstration of my learning, and the project's complexity will evolve as my overall experience grows.


### Background

Websites implement security measures to safeguard against fraud and abuse by distinguishing between human users and automated bots. Google's reCAPTCHA v2 incorporates an **invisible reCAPTCHA** as its base layer, which automatically analyzes user actions (mouse movements, keyboard inputs, human-like patterns, and signals) to determine the likelihood of the user being human.

If the system is uncertain if the user is human, it presents additional verification challenges. One such challenge involves selecting images based on a specific prompt, such as "select all images with cars" or "select all images containing street signs."


### Requirements
1. The superuser can upload images. The app manages the formatting and display logic, however, the superuser must manually choose which objects the Captcha tests for. 
2. Users can view a list of captcha (whether signed in or not).
3. Users can solve individual captchas or choose to solve a series of unique ones (signing in ensures no repetition for a given account).


### Detailed Design

##### 1. Uploading Captcha
Superusers and admins, using Django's admin interface, can contribute images for captchas. The admin site, being modular, has been altered structurally and functionally: using Django's signal dispatcher, the image is automatically validated upon captcha creation, after which a number related models (the *ImageSlice* model representing a single image of the Captcha grid) are created. The manual, and perhaps tedious, part of this process is selecting which images in the grid display the object the Captcha requires you to select. In the future, I'd like for some type of computer vision to solve this.

##### 2. Captcha
The user is presented with a series of increasingly complex captchas. Successive captchas are loaded asynchronously with Vanilla JS through DOM manipulation. User responses are saved to ensure no user is served with the same captcha again. Users can sign up with a unique username. Django's password validation is disabled to simplify account creation, considering users may attempt the captcha multiple times.


### Future Work:
1. Automatically identify objects and provide admins the option to choose which object within the image should the captcha evaluate for. This is a long-term goal that I'll constantly be moving towards.
2. At this moment, only a single *type* of captcha has been implemented. I have two more captcha-types in the pipeline. 
3. Provide the option for users to report if a captcha has not been evaluated properly. When paired with #1, it should help aggregate public feedback on how much of this captcha creation process can be automated.
4. [Done 3/24] Speed: I've incorporated asynchronous Javascript to smooth out the experience. However, in production, image load times are slow and server response times are noticeably much slower. I want to explore switching to a geographically closer compute instance (like EC2 in Mumbai, compared to the current US-based Heroku). Additionally, its worth seeing if a CDN [in front of](https://whitenoise.readthedocs.io/en/stable/#isn-t-serving-static-files-from-python-horribly-inefficient) WhiteNoise will further enhance performance. 
