// ========================================
// FILE UPLOAD
// ========================================

const fileInput =
    document.getElementById("fileInput");

const uploadButton =
    document.getElementById("uploadButton");

const uploadStatus =
    document.getElementById("uploadStatus");


uploadButton.addEventListener(
    "click",
    async () => {

        const file =
            fileInput.files[0];


        // ------------------------------
        // Make sure a file was selected
        // ------------------------------

        if (!file) {

            uploadStatus.textContent =
                "Please select a file first.";

            return;
        }


        // ------------------------------
        // Prepare multipart form data
        // ------------------------------

        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );


        uploadButton.disabled = true;

        uploadStatus.textContent =
            "Uploading and processing...";


        try {

            // --------------------------
            // Send file to FastAPI
            // --------------------------

            const response =
                await fetch(
                    "/ingest",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Upload failed."
                );
            }


            // --------------------------
            // Successful upload
            // --------------------------

            uploadStatus.textContent =
                `✓ ${data.message} ` +
                `(${data.chunks} chunks created)`;


        } catch (error) {

            uploadStatus.textContent =
                `❌ ${error.message}`;

        } finally {

            uploadButton.disabled = false;

        }

    }
);



// ========================================
// ASK QUESTION
// ========================================

const questionInput =
    document.getElementById(
        "questionInput"
    );

const askButton =
    document.getElementById(
        "askButton"
    );

const answer =
    document.getElementById(
        "answer"
    );

const sources =
    document.getElementById(
        "sources"
    );


askButton.addEventListener(
    "click",
    async () => {

        const question =
            questionInput.value.trim();


        // ------------------------------
        // Validate question
        // ------------------------------

        if (!question) {

            answer.textContent =
                "Please enter a question.";

            return;
        }


        askButton.disabled = true;

        answer.textContent =
            "DocMind is thinking...";


        sources.innerHTML =
            "<p class='muted'>Loading sources...</p>";


        try {

            // --------------------------
            // Send question to FastAPI
            // --------------------------

            const response =
                await fetch(
                    "/ask",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            question: question
                        })
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Request failed."
                );
            }


            // --------------------------
            // Display answer
            // --------------------------

            answer.textContent =
                data.answer;


            // --------------------------
            // Display sources
            // --------------------------

            sources.innerHTML = "";


            if (
                !data.sources ||
                data.sources.length === 0
            ) {

                sources.innerHTML =
                    "<p class='muted'>" +
                    "No sources found." +
                    "</p>";

                return;
            }


            data.sources.forEach(
                (source, index) => {

                    const sourceElement =
                        document.createElement(
                            "div"
                        );

                    sourceElement.className =
                        "source";


                    sourceElement.innerHTML = `
                        <strong>
                            [${index + 1}]
                            ${source.source}
                        </strong>

                        <small>
                            Chunk:
                            ${source.chunk_index}
                            &nbsp; | &nbsp;
                            Score:
                            ${source.score.toFixed(4)}
                        </small>
                    `;


                    sources.appendChild(
                        sourceElement
                    );

                }
            );


        } catch (error) {

            answer.textContent =
                `❌ ${error.message}`;

            sources.innerHTML = "";

        } finally {

            askButton.disabled = false;

        }

    }
);