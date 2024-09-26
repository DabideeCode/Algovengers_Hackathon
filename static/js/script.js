function uploadResume() {
    const fileInput = document.getElementById('resumeUpload');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please upload a resume file.');
        return;
    }

    // Simulate the transformation process (you would replace this with your actual transformation logic)
    alert(`Resume uploaded: ${file.name}`);

    // TODO: Implement transformation logic here (API call or demo preview)
    
    // After transformation, generate a transformed file and trigger the download
    transformAndDownload(file);
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
