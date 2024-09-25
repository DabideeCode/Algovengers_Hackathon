function uploadResume() {
    const fileInput = document.getElementById('resumeUpload');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please upload a resume file.');
        return;
    }

    // Change the button text to "Converting..."
    const transformButton = document.querySelector('.transform-button');
    transformButton.textContent = "Converting...";
    transformButton.disabled = true;  // Disable the button during conversion

    // Simulate the transformation process (you would replace this with your actual transformation logic)
    setTimeout(() => {
        alert(`Resume uploaded: ${file.name}`);

        // Simulate the conversion and trigger the download
        transformAndDownload(file);

        // Revert the button text to "Show Live Demo" after conversion completes
        transformButton.textContent = "Show Live Demo";
        transformButton.disabled = false;  // Re-enable the button
    }, 2000);  // Simulate a 2-second delay for conversion (replace this with actual conversion logic)
}

function transformAndDownload(file) {
    // Simulate transformed file content - replace this with the actual transformed data
    const transformedContent = `Transformed resume for: ${file.name}\n\n[Transformed content here]`;

    // Create a Blob with transformed content
    const blob = new Blob([transformedContent], { type: "text/plain" });

    // Create a URL for the blob
    const url = window.URL.createObjectURL(blob);

    // Create an anchor element to trigger download
    const a = document.createElement("a");
    a.href = url;
    a.download = `Transformed_${file.name}`;  // The downloaded file's name

    // Append the anchor to the body (necessary for Firefox)
    document.body.appendChild(a);

    // Programmatically click the anchor to trigger the download
    a.click();

    // Clean up: remove the anchor element and revoke the object URL
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}



document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;

    const formData = {
        name: name,
        email: email,
        message: message
    };

    fetch('https://script.google.com/macros/s/AKfycbzeWrE8nMKycJFesrbiw-UUXni5-M4YtxbFfiviee3osRfqSoo28pTfX_i7jhPHKRLeAg/exec', { 
        method: 'POST',
        mode: 'no-cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    }).then(response => {
        document.getElementById('responseMessage').textContent = "Message sent successfully!";
        document.getElementById('contactForm').reset();
    }).catch(error => {
        document.getElementById('responseMessage').textContent = "Failed to send message.";
        console.error('Error:', error);
    });
});
