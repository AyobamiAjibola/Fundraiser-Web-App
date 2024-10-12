// document.addEventListener('DOMContentLoaded', function(){
//     console.log(alert("Hello guys"))
// })

// document.addEventListener('DOMContentLoaded', function(event) {
//   function handleModalContent(event) {
//     const targetId = event.detail.target.id;
//     if (targetId === "profile-dialog") {
      
//     }
//   }
//   htmx.on("htmx:afterSwap", handleModalContent);
// });

// document.addEventListener('DOMContentLoaded', (event) => {
//     setTimeout(() => {
//         const message = document.getElementById('err-msg');
//         message.style.opacity = '0';
//         // Optional: hide the element after fade out
//         setTimeout(() => {
//             message.style.display = 'none';
//         }, 1000); // match this duration with the fade-out transition duration
//     }, 3000); // Time in milliseconds (5000ms = 5 seconds)
// });

// document.addEventListener('DOMContentLoaded', (event) => {
//     setTimeout(() => {
//         const message = document.getElementById('validation');
//         message.style.opacity = '0';
//         // Optional: hide the element after fade out
//         setTimeout(() => {
//             message.style.display = 'none';
//         }, 1000); // match this duration with the fade-out transition duration
//     }, 3000); // Time in milliseconds (5000ms = 5 seconds)
// });

document.addEventListener("DOMContentLoaded", function () {
  const modal = new bootstrap.Modal(document.getElementById("modal"));
  const profileModal = new bootstrap.Modal(document.getElementById("profile-modal"));
  const fundModal = new bootstrap.Modal(document.getElementById("fund-modal"));

  function handleModalContent(event) {
      const targetId = event.detail.target.id;

      if (targetId === "dialog") {
        modal.show();
      } else if (targetId === "profile-dialog") {
        profileModal.show();
      } else if (targetId === "fund-dialog") {
        fundModal.show();
      }
  }

  function handleBeforeSwap(event) {
      const targetId = event.detail.target.id;

      if (targetId === "dialog" && !event.detail.xhr.response) {
        modal.hide();
        event.detail.shouldSwap = false;
      } else if (targetId === "profile-dialog" && !event.detail.xhr.response) {
        profileModal.hide();
        event.detail.shouldSwap = false;
      } else if (targetId === "fund-dialog" && !event.detail.xhr.response) {
        fundModal.hide();
        event.detail.shouldSwap = false;
      } 
  }

  function handleHidden() {
      const dialog = document.getElementById("dialog");
      const profileDialog = document.getElementById("profile-dialog");
      const fundDialog = document.getElementById("fund-dialog");

      if (dialog) {
        dialog.innerHTML = "";
      }
      if (profileDialog) {
        profileDialog.innerHTML = "";
      }
      if (fundDialog) {
        fundDialog.innerHTML = "";
      }
  }

  htmx.on("htmx:afterSwap", handleModalContent);
  htmx.on("htmx:beforeSwap", handleBeforeSwap);
  htmx.on("hidden.bs.modal", handleHidden);
});

document.addEventListener("DOMContentLoaded", function() {
  const username = document.getElementById('username')
  function capitalizeFirstLetter(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
  }
  const capitalize = capitalizeFirstLetter(username.textContent);
  username.textContent = capitalize;
})

document.addEventListener("DOMContentLoaded", function() {
  const imgElement = document.querySelector('.profile-img');
  const fallbackElement = document.querySelector('.fallback-initials');

  if (!imgElement.src) {
    imgElement.style.display = 'none';
    fallbackElement.style.display = 'flex';
  } else {
    imgElement.addEventListener('error', function() {
        imgElement.style.display = 'none';
        fallbackElement.style.display = 'flex';
    });
  }

  imgElement.addEventListener('load', function() {
    if (imgElement.src) {
      fallbackElement.style.display = 'none';
    } else {
      fallbackElement.style.display = 'flex';
    }
  });
});


