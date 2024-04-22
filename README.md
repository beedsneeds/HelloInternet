
## CaptchaPractice


Auto-generate captcha based on your own images and solve the ones the community creates! 

The project is live on [render](https://hellointernet.onrender.com/captchapractice/).

Runs the [YOLO8](https://github.com/ultralytics/ultralytics/) segmentation model to identify objects and provide customization options during the captcha creation process. 

---

#### Detailed Functionality

##### 1. Creating Captcha

Users can upload an image of specific dimensions (1:1 aspect ratio). The uploaded image is processed using the pre-trained object detection model YOLO8, which identifies and highlights objects within the images. Users are then presented with a list of detected objects to choose from.  This selection determines the object that users will need to identify in the captcha. Users can also specify additional parameters such as the grid layout (i.e., how the captcha will be divided into smaller sections) and the perceived difficulty level of the captcha. Based on the user's selections and specified parameters, the captcha is generated and displayed. Additionally, a link to solve the captcha is provided.

##### 2. Solving Captcha

Users are presented with a series of four captchas, each progressively more challenging than the last. To ensure variety, responses to captchas are saved, preventing users from encountering the same captcha multiple times. To simplify account creation, all password validation is disabled, as the users are encouraged to attempt the captchas multiple times. This approach facilitates a smoother user experience, encouraging engagement with the captcha challenges without unnecessary barriers.

---

#### Design Documentation

---

<details>
    <summary><h3>Future Work</h3></summary>
    <li>
    At this moment, only a single *type* of captcha has been implemented. I have two more captcha-types in the pipeline. 
    </li>
    <li>
    Provide the option for users to report if a captcha has not been evaluated properly.
    </li>
    <li>
    [In Progress] Speed: I've incorporated asynchronous Javascript to smooth out the experience. However, in production, image load times are slow and server response times are noticeably much slower. I want to explore switching to a geographically closer compute instance (like EC2 in Mumbai, compared to the current US-based Heroku). Additionally, its worth seeing if a CDN [in front of](https://whitenoise.readthedocs.io/en/stable/#isn-t-serving-static-files-from-python-horribly-inefficient) WhiteNoise will further enhance performance.
    </li>

</details>

