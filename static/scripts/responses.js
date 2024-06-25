function getBotResponse(input) {
  const chatbotResUrl = "/ask";  // Ensure this matches your Django URL configuration
  const data = {
    user_query: input,
    language: "english"  // Set the language you want the bot to respond in
  };

  $.ajax({
    type: "POST",
    url: chatbotResUrl,
    data: JSON.stringify(data),
    contentType: "application/json",
    success: function (response) {
      let botHtml = '<p class="botText"><span>' + response.ai_response + '</span></p>';
      $("#chatbox").append(botHtml);
      console.log(response.ai_response);

      // Attach click event listener to the newly added botText element
      attachCopyEventListener();
    },
    error: function (response) {
      console.log(response);
    },
  });
}

function attachCopyEventListener() {
  let botTextElements = document.querySelectorAll('.botText');
  
  // Loop through each element and attach a click event listener
  botTextElements.forEach(function (element) {
    element.addEventListener('click', function () {
      // Get the text content of the clicked p tag
      let text = this.querySelector('span').textContent;
      // Copy the text to clipboard
      navigator.clipboard.writeText(text)
        .then(function() {
          // Alert the user that the text has been copied
          alert("Copied to clipboard: " + text);
        })
        .catch(function(error) {
          console.error('Failed to copy text: ', error);
        });
    });
  });
}

// Call this function once initially to attach event listeners to any pre-existing botText elements
attachCopyEventListener();
