
// Search button functionality
document.getElementById("search-button").addEventListener("click", function() {
    var inputText = document.getElementById("input-text").value;
    var outputContainer = document.getElementById("output-container");
    var outputText = document.getElementById("output-text");
    var transcriptionHeader = document.getElementById("phonetic-transcription");
  
    if (inputText.trim() !== "") {
      // Send the input text to the Flask backend
      fetch('/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: inputText })
      })
      .then(response => response.json())
      .then(data => {
        // Ensure HTML output is rendered
        outputText.innerHTML = data.output.replace(/\n/g, "<br>"); // Display the output from the server with HTML formatting
        outputContainer.style.display = "block"; // Show the box with the output
        transcriptionHeader.style.display = "block"; // Show the header
                
        // Show feedback form after output is generated
        setTimeout(function() {
          document.getElementById("surveyModal").style.display = "block"; // Show modal
          document.getElementById("overlay").style.display = "block"; // Show overlay
        }, 10000); // 10 seconds after output
      })
      .catch(error => {
        console.error('Error:', error);
        outputText.innerText = "An error occurred while processing your request.";
        outputContainer.style.display = "block"; // Show the box with the error message
      });
    } else {
      outputContainer.style.display = "none"; // Hide the box if no input is given
      transcriptionHeader.style.display = "none"; // Hide the header
    }
  });
  
  // Clear button functionality
  document.getElementById("clear-button").addEventListener("click", function() {
    document.getElementById("input-text").value = "";
    document.getElementById("output-container").style.display = "none"; // Hide the output container
    document.getElementById("phonetic-transcription").style.display = "none"; // Hide the header
  });
  
  // Copy button functionality
  document.getElementById("copy-button").addEventListener("click", function() {
    var outputTextElement = document.getElementById("output-text");
  
    // Create a range and select the contents of the output-text element
    var range = document.createRange();
    range.selectNodeContents(outputTextElement);
  
    // Clear any previous selections
    var selection = window.getSelection();
    selection.removeAllRanges();
  
    // Add the range to the selection (mimicking manual selection)
    selection.addRange(range);
  
    try {
      // Execute the copy command to copy the selected content
      var successful = document.execCommand('copy');
      if (successful) {
        alert('Text copied to clipboard!');
      } else {
        alert('Failed to copy text.');
      }
    } catch (err) {
      console.error('Error copying text: ', err);
    }
  
    // Clear the selection after copying
    selection.removeAllRanges();
  });
  
  // PDF Button functionality
  document.getElementById("pdf-button").addEventListener("click", function() {
    var outputTextElement = document.getElementById("output-text");
  
    // Clone the element to prevent modifying the original
    var clonedOutput = outputTextElement.cloneNode(true);
  
    // Remove any background color from the cloned content (if present)
    clonedOutput.style.backgroundColor = "transparent";
    clonedOutput.style.width = '100%'; // Ensures it uses the full width available
  
    // Configure the PDF options (margins, filename, etc.)
    var pdfOptions = {
      margin: 0.5, // Adjust margins to fit content better
      filename: 'output.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 }, // Adjust scale for better quality
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
  
    // Generate the PDF
    html2pdf().from(clonedOutput).set(pdfOptions).save();
  });
  