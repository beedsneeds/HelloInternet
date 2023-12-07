
console.log("do we even reach this")


async function submitForm(event) {
    event.preventDefault();

    const csrfToken = getCookie('csrftoken');
    const imageId = JSON.parse(document.querySelector("#image_id").textContent);
    const postURL = `/captchapractice/${imageId}/`;

    const form = document.querySelector('#response-form');
    const formData = new FormData(form);
    const formDataArray = [];
    formData.forEach((value, key) => {
        if (key === "selected_images") {
            formDataArray.push(value);
        }
    });
    const jsonData = JSON.stringify(formDataArray);

    try {
        const response = await fetch(postURL, {
            method: 'POST',
            body: jsonData,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            mode: 'same-origin'
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const responseJson = await response.json();
        responseHTML = responseJson.html

        renderPostContents(responseHTML, '#post-contents', '#get-contents');

    } catch (error) {
        console.error('Error:', error);
    }
}

// Loads the contents within some 'parentSelector' with 'fragmentSelector'
function renderPostContents(htmldoc, fragmentSelector, parentSelector) {
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = htmldoc;

    const parentDiv = document.querySelector(parentSelector);
    const contentFragment = tempContainer.querySelector(fragmentSelector);

    parentDiv.innerHTML = '';
    parentDiv.appendChild(contentFragment);
}


// Copied from django's documentation on how to use csrf protection with AJAX
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


