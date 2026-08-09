const form = document.getElementById("prompt-form");
const promptInput = document.getElementById("prompt");
const templateInput = document.getElementById("template");
const submitButton = document.getElementById("submit-btn");
const responseBox = document.getElementById("response");
const message = document.getElementById("message");
const providerBadge = document.getElementById("provider-badge");
const count = document.getElementById("count");

promptInput.addEventListener("input", () => {
    count.textContent = promptInput.value.length;
});

function showMessage(text, type = "error") {
    message.textContent = text;
    message.className = `message ${type}`;
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const prompt = promptInput.value.trim();
    const template = templateInput.value;

    message.className = "message hidden";
    responseBox.textContent = "Processing...";
    providerBadge.className = "badge hidden";
    submitButton.disabled = true;
    submitButton.textContent = "Processing...";

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 25000);

        const res = await fetch("/api/prompt", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({prompt, template}),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        const data = await res.json();

        if (!res.ok || !data.ok) {
            responseBox.textContent = "No response.";
            showMessage(data.error || "Request failed.", "error");
            return;
        }

        responseBox.textContent = data.response;
        providerBadge.textContent = data.provider_mode;
        providerBadge.className = "badge";
        showMessage("Prompt processed successfully.", "success");
    } catch (error) {
        responseBox.textContent = "No response.";

        if (error.name === "AbortError") {
            showMessage("The request took too long. Please try again.", "error");
        } else {
            showMessage("Could not connect to the application.", "error");
        }
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Send Prompt";
    }
});
