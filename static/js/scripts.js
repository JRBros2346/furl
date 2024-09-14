// Asynchronously copies the full URL, including the protocol, host, and furl, to the clipboard
async function copyToClipboard(furl) {
  try {
    // Use the Clipboard API to copy the full URL (protocol + host + furl) to the clipboard
    await navigator.clipboard.writeText(location.protocol + '//' + location.host + '/' + furl);
      alert('URL copied to clipboard');  // Display an alert to the user that the URL has been copied
  } catch (err) {
    console.error('Could not copy text: ', err);  // Log any error if the copy fails
  }
}

// Asynchronously prepends the protocol and host to all URLs in elements with the class 'url'
async function addHost() {
  // Iterate over each element with the class 'url'
  for (const cell of document.getElementsByClassName('url')) {
    // Prepend the protocol and host (e.g., http://localhost/) to the URL in each element
    cell.prepend(location.protocol + '//' + location.host + '/');
  }
  // If an element with the id 'link' exists, prepend the protocol and host to its content as well
  document.getElementById("link")?.prepend(location.protocol + '//' + location.host + '/');
}

// Call the addHost function when the script runs to update URLs on page load
addHost();
