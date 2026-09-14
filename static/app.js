const fileInput = document.getElementById("fileInput");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");

const answer = document.getElementById("answer");
const sources = document.getElementById("sources");


/*
--------------------------------------------------
UPLOAD DOCUMENT
--------------------------------------------------
Sends the selected document to FastAPI.

Flow:

Browser
   ↓
POST /ingest
   ↓
FastAPI
   ↓
load → chunk → embed → Qdrant
--------------------------------------------------
*/

uploadButton.addEventListener("click", async () => {

    const file = fileInput.files[0];

    if (!file) {
        uploadStatus.textContent = "Please select a document first.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadButton.disabled = true;
    uploadButton.textContent = "Uploading...";
    uploadStatus.textContent = "Processing document...";

    try {

        const response = await fetch("/ingest", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Upload failed.");
        }

        uploadStatus.textContent =
            `✓ ${data.filename} uploaded successfully — ${data.chunks} chunk(s) stored.`;

    } catch (error) {

        uploadStatus.textContent =
            `✕ ${error.message}`;

    } finally {

        uploadButton.disabled = false;
        uploadButton.textContent = "Upload Document";
    }
});


/*
--------------------------------------------------
ASK DOCMIND
--------------------------------------------------
Sends the user's question to FastAPI.

Flow:

Question
   ↓
POST /ask
   ↓
Embedding
   ↓
Qdrant retrieval
   ↓
Relevant context
   ↓
LLM
   ↓
Answer + sources
--------------------------------------------------
*/

askButton.addEventListener("click", askQuestion);


async function askQuestion() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    const conversation =
        document.getElementById("conversation");


    /*
    ------------------------------------------
    ADD USER MESSAGE
    ------------------------------------------
    */

    const userMessage = document.createElement("div");

    userMessage.className = "chat-message user-message";

    userMessage.innerHTML = `
        <div class="chat-label">
            You
        </div>

        <div class="user-bubble">
            ${escapeHtml(question)}
        </div>
    `;

    conversation.appendChild(userMessage);


    /*
    ------------------------------------------
    ADD LOADING MESSAGE
    ------------------------------------------
    */

    const aiMessage = document.createElement("div");

    aiMessage.className = "chat-message ai-message";

    aiMessage.innerHTML = `
        <div class="chat-label">
            🧠 DocMind
        </div>

        <div class="ai-bubble">
            <div class="chat-loading">
                Searching your documents...
            </div>
        </div>
    `;

    conversation.appendChild(aiMessage);


    /*
    ------------------------------------------
    SCROLL TO NEW MESSAGE
    ------------------------------------------
    */

    aiMessage.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });


    /*
    ------------------------------------------
    DISABLE BUTTON
    ------------------------------------------
    */

    askButton.disabled = true;
    askButton.textContent = "Thinking...";


    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail || "Something went wrong."
            );
        }


        /*
        ------------------------------------------
        DISPLAY ANSWER
        ------------------------------------------
        */

        const aiBubble =
            aiMessage.querySelector(".ai-bubble");

        aiBubble.innerHTML =
            formatAnswer(data.answer);


        /*
        ------------------------------------------
        ADD SOURCES
        ------------------------------------------
        */

        if (data.sources && data.sources.length > 0) {

            const sourceBlock =
                document.createElement("div");

            sourceBlock.className = "message-sources";

            sourceBlock.innerHTML = `
                <div class="message-sources-title">
                    📚 Sources
                </div>
            `;


            data.sources.forEach((source) => {

                const card =
                    document.createElement("div");

                card.className = "source-card";

                card.innerHTML = `
                    <div class="source-title">
                        📄 ${escapeHtml(source.source)}
                    </div>

                    <div class="source-info">
                        Chunk ${source.chunk_index}
                        <span>•</span>
                        Hybrid retrieval
                    </div>
                `;

                sourceBlock.appendChild(card);
            });


            aiBubble.appendChild(sourceBlock);
        }


        /*
        ------------------------------------------
        CLEAR QUESTION BOX
        ------------------------------------------
        */

        questionInput.value = "";


        /*
        ------------------------------------------
        SCROLL TO ANSWER
        ------------------------------------------
        */

        aiMessage.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });


    } catch (error) {

        const aiBubble =
            aiMessage.querySelector(".ai-bubble");

        aiBubble.innerHTML = `
            <div class="error">
                ✕ ${escapeHtml(error.message)}
            </div>
        `;

    } finally {

        askButton.disabled = false;
        askButton.textContent = "Ask DocMind";
    }
}


/*
--------------------------------------------------
BASIC MARKDOWN FORMATTER
--------------------------------------------------

Your backend already returns things like:

## Answers

**Product name:** AcmeAI

We convert the most common Markdown
elements into HTML.

This is intentionally lightweight.
We don't need a large frontend framework.
--------------------------------------------------
*/

function formatAnswer(text) {

    if (!text) {
        return "<p>No answer was returned.</p>";
    }

    let html = escapeHtml(text);

    // Headings
    html = html.replace(
        /^### (.*)$/gm,
        "<h4>$1</h4>"
    );

    html = html.replace(
        /^## (.*)$/gm,
        "<h3>$1</h3>"
    );

    html = html.replace(
        /^# (.*)$/gm,
        "<h2>$1</h2>"
    );

    // Bold
    html = html.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    // Bullet points
    html = html.replace(
        /^- (.*)$/gm,
        "<li>$1</li>"
    );

    html = html.replace(
        /(<li>.*<\/li>)/gs,
        "<ul>$1</ul>"
    );

    // New lines
    html = html.replace(
        /\n/g,
        "<br>"
    );

    return html;
}


/*
--------------------------------------------------
SECURITY HELPER

Never insert raw user/backend text directly
into innerHTML.

This prevents HTML injection problems.
--------------------------------------------------
*/

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


/*
--------------------------------------------------
ENTER KEY SUPPORT

Ctrl + Enter → Ask question

This makes the interface feel more like
an actual AI assistant.
--------------------------------------------------
*/

questionInput.addEventListener("keydown", (event) => {

    if (event.ctrlKey && event.key === "Enter") {
        askQuestion();
    }

});