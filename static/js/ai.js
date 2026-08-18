document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       ELEMENTS
       ===================================================== */

    const imageInput =
        document.getElementById("imageInput");

    const uploadArea =
        document.getElementById("uploadArea");

    const previewContainer =
        document.getElementById("previewContainer");

    const imagePreview =
        document.getElementById("imagePreview");

    const detectButton =
        document.getElementById("detectButton");

    const loadingContainer =
        document.getElementById("loadingContainer");

    const resultContainer =
        document.getElementById("resultContainer");

    const resultIcon =
        document.getElementById("resultIcon");

    const prediction =
        document.getElementById("prediction");

    const confidence =
        document.getElementById("confidence");

    const plantName =
        document.getElementById("plantName");

    const plantMyanmar =
        document.getElementById("plantMyanmar");

    const diseaseName =
        document.getElementById("diseaseName");

    const diseaseMyanmar =
        document.getElementById("diseaseMyanmar");

    const resultMessage =
        document.getElementById("resultMessage");

    const recommendationBox =
        document.getElementById("recommendationBox");

    const recommendationTitle =
        document.getElementById("recommendationTitle");

    const recommendationIcon =
        document.getElementById("recommendationIcon");

    const recommendationText =
        document.getElementById("recommendationText");

    const recommendationMyanmarContainer =
        document.getElementById(
            "recommendationMyanmarContainer"
        );

    const recommendationMyanmar =
        document.getElementById("recommendationMyanmar");

    const newScanButton =
        document.getElementById("newScanButton");

    const errorContainer =
        document.getElementById("errorContainer");

    const errorMessage =
        document.getElementById("errorMessage");

    const retryButton =
        document.getElementById("retryButton");


    let selectedFile = null;



    /* =====================================================
       MYANMAR PLANT NAMES
       ===================================================== */

    const MYANMAR_PLANT_NAMES = {

        "Apple": "ပန်းသီး",

        "Blueberry": "ဘလူးဘယ်ရီ",

        "Cherry": "ချယ်ရီ",

        "Corn": "ပြောင်း",

        "Grape": "စပျစ်",

        "Orange": "လိမ္မော်",

        "Peach": "မက်မွန်",

        "Bell Pepper": "ငရုတ်ပွ",

        "Potato": "အာလူး",

        "Raspberry": "ရက်စ်ဘယ်ရီ",

        "Soybean": "ပဲပုပ်",

        "Squash": "ဖရုံ",

        "Strawberry": "စတော်ဘယ်ရီ",

        "Tomato": "ခရမ်းချဉ်သီး"

    };



    /* =====================================================
       MYANMAR DISEASE NAMES
       ===================================================== */

    const MYANMAR_DISEASE_NAMES = {

        "Apple Scab":
            "ပန်းသီးအရွက်ပြောက်ရောဂါ",

        "Black Rot":
            "အမည်းပုပ်ရောဂါ",

        "Cedar Apple Rust":
            "Cedar Apple Rust ရောဂါ",

        "Healthy":
            "ကျန်းမာ",

        "Powdery Mildew":
            "အမှုန့်မှိုရောဂါ",

        "Cercospora Leaf Spot / Gray Leaf Spot":
            "Cercospora အရွက်ပြောက် / မီးခိုးရောင်အရွက်ပြောက်ရောဂါ",

        "Common Rust":
            "သံချေးရောဂါ",

        "Northern Leaf Blight":
            "မြောက်ပိုင်းအရွက်ခြောက်ရောဂါ",

        "Esca (Black Measles)":
            "Esca (Black Measles) ရောဂါ",

        "Leaf Blight (Isariopsis Leaf Spot)":
            "အရွက်ခြောက်ရောဂါ",

        "Huanglongbing (Citrus Greening)":
            "လိမ္မော်စိမ်းရောင်ရောဂါ",

        "Bacterial Spot":
            "ဘက်တီးရီးယားအရွက်ပြောက်ရောဂါ",

        "Early Blight":
            "အရွက်စောခြောက်ရောဂါ",

        "Late Blight":
            "အရွက်နောက်ကျခြောက်ရောဂါ",

        "Leaf Mold":
            "အရွက်မှိုရောဂါ",

        "Septoria Leaf Spot":
            "Septoria အရွက်ပြောက်ရောဂါ",

        "Spider Mites (Two-spotted Spider Mite)":
            "ပင့်ကူနီပိုးရောဂါ",

        "Target Spot":
            "Target Spot အရွက်ပြောက်ရောဂါ",

        "Tomato Yellow Leaf Curl Virus":
            "ခရမ်းချဉ်သီး အရွက်ဝါကောက်ဗိုင်းရပ်စ်ရောဂါ",

        "Tomato Mosaic Virus":
            "ခရမ်းချဉ်သီး Mosaic ဗိုင်းရပ်စ်ရောဂါ",

        "Leaf Scorch":
            "အရွက်လောင်ရောဂါ",

        "No Leaf Detected":
            "အရွက်မတွေ့ရှိပါ"

    };



    /* =====================================================
       IMAGE SELECTED
       ===================================================== */

    imageInput.addEventListener(
        "change",
        function () {

            const file = this.files[0];

            if (!file) {
                return;
            }


            if (!file.type.startsWith("image/")) {

                showError(
                    "Please select a valid image file."
                );

                return;
            }


            selectedFile = file;


            const reader =
                new FileReader();


            reader.onload =
                function (event) {

                    imagePreview.src =
                        event.target.result;

                    uploadArea.style.display =
                        "none";

                    previewContainer.style.display =
                        "block";

                    resultContainer.style.display =
                        "none";

                    errorContainer.style.display =
                        "none";
                };


            reader.readAsDataURL(file);

        }
    );



    /* =====================================================
       DETECT
       ===================================================== */

    detectButton.addEventListener(
        "click",
        async function () {

            if (!selectedFile) {

                showError(
                    "Please select an image first."
                );

                return;
            }


            uploadArea.style.display =
                "none";

            previewContainer.style.display =
                "none";

            resultContainer.style.display =
                "none";

            errorContainer.style.display =
                "none";

            loadingContainer.style.display =
                "block";


            const formData =
                new FormData();


            formData.append(
                "image",
                selectedFile
            );


            try {

                const response =
                    await fetch(
                        "/predict",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.error ||
                        "Unable to analyze image."
                    );

                }


                showResult(data);

            }


            catch (error) {

                console.error(
                    "AI detection error:",
                    error
                );


                showError(
                    error.message ||
                    "Something went wrong while analyzing the image."
                );

            }


            finally {

                loadingContainer.style.display =
                    "none";

            }

        }
    );



    /* =====================================================
       FORMAT WORDS
       ===================================================== */

    function formatWords(text) {

        if (!text) {
            return "";
        }


        return text
            .replace(/_/g, " ")
            .replace(/\s+/g, " ")
            .trim()
            .replace(
                /\b\w/g,
                function (letter) {
                    return letter.toUpperCase();
                }
            );

    }



    /* =====================================================
       FORMAT PREDICTION
       ===================================================== */

    function formatPrediction(
        predictionText
    ) {

        if (!predictionText) {

            return {
                plant: "Unknown Plant",
                condition: "Unknown Condition"
            };

        }


        const parts =
            predictionText.split("___");


        if (parts.length >= 2) {

            return {

                plant:
                    formatWords(parts[0]),

                condition:
                    formatWords(
                        parts
                            .slice(1)
                            .join(" ")
                    )

            };

        }


        return {

            plant: "",

            condition:
                formatWords(
                    predictionText
                )

        };

    }



    /* =====================================================
       GET MYANMAR PLANT NAME
       ===================================================== */

    function getMyanmarPlantName(
        plant
    ) {

        if (
            MYANMAR_PLANT_NAMES[plant]
        ) {

            return MYANMAR_PLANT_NAMES[
                plant
            ];

        }


        return plant || "-";

    }



    /* =====================================================
       GET MYANMAR DISEASE NAME
       ===================================================== */

    function getMyanmarDiseaseName(
        disease
    ) {

        if (
            MYANMAR_DISEASE_NAMES[disease]
        ) {

            return MYANMAR_DISEASE_NAMES[
                disease
            ];

        }


        return disease || "-";

    }



    /* =====================================================
       SHOW RESULT
       ===================================================== */

    function showResult(data) {

        resultContainer.style.display =
            "block";


        const formatted =
            formatPrediction(
                data.prediction
            );


        const diseaseInfo =
            data.disease_info || {};


        const predictionType =
            diseaseInfo.type ||
            (
                data.is_healthy
                    ? "healthy"
                    : "disease"
            );



        /* =================================================
           ICON
           ================================================= */

        const icon =
            diseaseInfo.icon ||
            "🌱";


        resultIcon.textContent =
            icon;



        /* =================================================
           PLANT NAME
           ================================================= */

        const plant =
            diseaseInfo.plant ||
            formatted.plant ||
            "-";


        const disease =
            diseaseInfo.disease ||
            formatted.condition ||
            "-";


        plantName.textContent =
            plant;


        diseaseName.textContent =
            disease;


        plantMyanmar.textContent =
            getMyanmarPlantName(
                plant
            );


        diseaseMyanmar.textContent =
            getMyanmarDiseaseName(
                disease
            );



        /* =================================================
           PREDICTION
           ================================================= */

        prediction.innerHTML =
            `<strong>${escapeHtml(plant)}</strong>
             <br>
             <span>${escapeHtml(disease)}</span>`;



        /* =================================================
           CONFIDENCE
           ================================================= */

        const confidenceValue =
            Number(
                data.confidence
            );


        confidence.textContent =
            Number.isFinite(
                confidenceValue
            )
                ? confidenceValue.toFixed(2) + "%"
                : "-";



        /* =================================================
           BACKGROUND / NO LEAF
           ================================================= */

        if (
            predictionType === "background"
        ) {

            resultIcon.textContent =
                diseaseInfo.icon ||
                "📷";


            resultMessage.textContent =
                "The AI could not detect a plant leaf in the uploaded image. Please upload a clear image of a plant leaf.";


            recommendationBox.style.display =
                "none";


            return;
        }



        /* =================================================
           HEALTHY
           ================================================= */

        if (
            predictionType === "healthy" ||
            data.is_healthy
        ) {

            resultMessage.textContent =
                "The AI model classified this plant leaf as healthy.";


            recommendationTitle.textContent =
                "Plant Care Recommendation";


            recommendationIcon.textContent =
                "🌿";


            const careText =
                diseaseInfo.care ||
                "Continue providing proper watering, sunlight, nutrition, and regular monitoring.";


            const careMyanmar =
                diseaseInfo.care_mm ||
                "သင့်လျော်သော ရေသွင်းခြင်း၊ နေရောင်ခြည်နှင့် အာဟာရများကို ပေးပြီး အပင်ကို ပုံမှန်စစ်ဆေးစောင့်ကြည့်ပါ။";


            recommendationText.textContent =
                careText;


            recommendationMyanmar.textContent =
                careMyanmar;


            recommendationMyanmarContainer.style.display =
                "block";


            recommendationBox.style.display =
                "block";


            return;
        }



        /* =================================================
           DISEASE
           ================================================= */

        resultMessage.textContent =
            "The AI model detected a possible plant disease. Consider checking the plant carefully.";


        recommendationTitle.textContent =
            "Treatment Recommendation";


        recommendationIcon.textContent =
            "🌿";


        const treatment =
            diseaseInfo.treatment ||
            "Consider consulting a local agricultural specialist for appropriate treatment.";


        const treatmentMyanmar =
            diseaseInfo.treatment_mm ||
            "သင့်လျော်သော ကုသမှုအတွက် ဒေသဆိုင်ရာ စိုက်ပျိုးရေးကျွမ်းကျင်သူနှင့် တိုင်ပင်ပါ။";


        recommendationText.textContent =
            treatment;


        recommendationMyanmar.textContent =
            treatmentMyanmar;


        recommendationMyanmarContainer.style.display =
            "block";


        recommendationBox.style.display =
            "block";

    }



    /* =====================================================
       ESCAPE HTML
       ===================================================== */

    function escapeHtml(text) {

        if (text === null || text === undefined) {
            return "";
        }


        return String(text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");

    }



    /* =====================================================
       NEW SCAN
       ===================================================== */

    newScanButton.addEventListener(
        "click",
        resetPage
    );


    retryButton.addEventListener(
        "click",
        resetPage
    );



    function resetPage() {

        selectedFile = null;


        imageInput.value =
            "";


        imagePreview.src =
            "";


        previewContainer.style.display =
            "none";


        loadingContainer.style.display =
            "none";


        resultContainer.style.display =
            "none";


        errorContainer.style.display =
            "none";


        recommendationBox.style.display =
            "none";


        uploadArea.style.display =
            "block";


        prediction.textContent =
            "-";


        confidence.textContent =
            "-";


        plantName.textContent =
            "-";


        plantMyanmar.textContent =
            "-";


        diseaseName.textContent =
            "-";


        diseaseMyanmar.textContent =
            "-";


        resultMessage.textContent =
            "";


        recommendationText.textContent =
            "";


        recommendationMyanmar.textContent =
            "";


        resultIcon.textContent =
            "🌱";

    }



    /* =====================================================
       ERROR
       ===================================================== */

    function showError(message) {

        loadingContainer.style.display =
            "none";


        previewContainer.style.display =
            "none";


        resultContainer.style.display =
            "none";


        recommendationBox.style.display =
            "none";


        errorContainer.style.display =
            "block";


        errorMessage.textContent =
            message;

    }

});