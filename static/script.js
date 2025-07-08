let selectedRole = "";

function selectRole(role) {
  selectedRole = role;
  document.getElementById("role-selection").classList.add("hidden");
  document.getElementById("auth-form").classList.remove("hidden");
  document.getElementById("form-title").innerText = `लगइन/ साइन अप as ${role}`;
}

function goBack() {
  document.getElementById("role-selection").classList.remove("hidden");
  document.getElementById("auth-form").classList.add("hidden");
  document.getElementById("message").innerText = "";
}

async function submitForm(action) {
  const username = document.getElementById("username").value;
  const phone = document.getElementById("phone").value;
  const password = document.getElementById("password").value;

  const payload = { username, phone, password };

  try {
    const res = await fetch(`/continue/${action}/${selectedRole}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || "Unknown error");
    document.getElementById("message").innerText = result.message;
  } catch (err) {
    document.getElementById("message").innerText = "❌ " + err.message;
  }
}
