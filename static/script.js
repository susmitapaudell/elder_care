let selectedRole = "";

function selectRole(role) {
  selectedRole = role;
  document.getElementById("role-selection").classList.add("hidden");
  document.getElementById("auth-form").classList.remove("hidden");
}

function goBack() {
  document.getElementById("auth-form").classList.add("hidden");
  document.getElementById("role-selection").classList.remove("hidden");
}

function submitForm(action) {
  const username = document.getElementById("username").value;
  const phone = document.getElementById("phone").value;
  const password = document.getElementById("password").value;

  fetch(`/auth/${action}/${selectedRole}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, phone, password })
  })
    .then(response => {
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        return response.json();
      }
    })
    .then(data => {
      if (data && data.message) {
        document.getElementById("message").textContent = data.message;
      }
    })
    .catch(err => {
      document.getElementById("message").textContent = "त्रुटि: " + err.message;
    });
}
