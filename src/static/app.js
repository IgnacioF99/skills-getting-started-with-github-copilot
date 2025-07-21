document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Limpiar lista y select antes de poblar
      activitiesList.innerHTML = "";
      // Mantener la opción por defecto en el select
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Poblar lista de actividades y select
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Participantes HTML
        let participantsHtml = "";
        if (details.participants.length > 0) {
          participantsHtml = `
            <div class="participants-section">
              <strong>Participants:</strong>
              <ul class="participants-list no-bullets">
                ${details.participants.map(email => `
                  <li>
                    <span class="participant-email">${email}</span>
                    <button class="remove-participant" data-activity="${name}" data-email="${email}" title="Remove participant">🗑️</button>
                  </li>
                `).join("")}
              </ul>
            </div>
          `;
        } else {
          participantsHtml = `
            <div class="participants-section">
              <strong>Participants:</strong>
              <p class="no-participants">No one has signed up yet.</p>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHtml}
        `;

        activitiesList.appendChild(activityCard);

        // Agregar opción al select
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Agregar manejador de eliminación a los botones
      document.querySelectorAll(".remove-participant").forEach(btn => {
        btn.addEventListener("click", async (e) => {
          const activity = btn.getAttribute("data-activity");
          const email = btn.getAttribute("data-email");
          try {
            const response = await fetch(`/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`, {
              method: "DELETE",
            });
            const result = await response.json();
            if (response.ok) {
              messageDiv.textContent = result.message || "Participant removed.";
              messageDiv.className = "success";
              fetchActivities();
            } else {
              messageDiv.textContent = result.detail || "Error removing participant.";
              messageDiv.className = "error";
            }
            messageDiv.classList.remove("hidden");
            setTimeout(() => {
              messageDiv.classList.add("hidden");
            }, 5000);
          } catch (error) {
            messageDiv.textContent = "Failed to remove participant. Please try again.";
            messageDiv.className = "error";
            messageDiv.classList.remove("hidden");
            setTimeout(() => {
              messageDiv.classList.add("hidden");
            }, 5000);
            console.error("Error removing participant:", error);
          }
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Actualiza la lista tras registro exitoso
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
