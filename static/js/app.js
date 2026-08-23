let currentMeetingId = null;

document.addEventListener("DOMContentLoaded", () => {
    loadMeetingHistory();
    setupEventListeners();
});

function setupEventListeners() {
    const dropZone = document.getElementById("dropZone");
    const audioInput = document.getElementById("audioFile");
    const uploadForm = document.getElementById("uploadForm");
    const refreshBtn = document.getElementById("refreshHistoryBtn");
    const deleteBtn = document.getElementById("deleteMeetingBtn");

    dropZone.addEventListener("click", () => audioInput.click());

    audioInput.addEventListener("change", () => {
        if (audioInput.files.length > 0) {
            document.getElementById("fileNameDisplay").textContent = audioInput.files[0].name;
        }
    });

    // Drag and drop support
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("border-indigo-500", "bg-indigo-50");
    });
    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("border-indigo-500", "bg-indigo-50");
    });
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("border-indigo-500", "bg-indigo-50");
        if (e.dataTransfer.files.length > 0) {
            audioInput.files = e.dataTransfer.files;
            document.getElementById("fileNameDisplay").textContent = e.dataTransfer.files[0].name;
        }
    });

    uploadForm.addEventListener("submit", handleMeetingUpload);
    refreshBtn.addEventListener("click", loadMeetingHistory);
    deleteBtn.addEventListener("click", handleDeleteMeeting);
}

async function handleMeetingUpload(e) {
    e.preventDefault();
    const audioInput = document.getElementById("audioFile");
    const titleInput = document.getElementById("meetingTitle");
    const processBtn = document.getElementById("processBtn");
    const loadingState = document.getElementById("loadingState");

    if (!audioInput.files || audioInput.files.length === 0) {
        alert("Please select an audio file to process.");
        return;
    }

    const formData = new FormData();
    formData.append("audio", audioInput.files[0]);
    if (titleInput.value.trim()) {
        formData.append("title", titleInput.value.trim());
    }

    // UI Loading State
    processBtn.disabled = true;
    loadingState.classList.remove("hidden");

    try {
        const response = await fetch("/api/v1/meetings/process", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Failed to process meeting.");
        }

        // Render newly created record
        renderMeetingDetails(result.data);
        await loadMeetingHistory();
        uploadForm.reset();
        document.getElementById("fileNameDisplay").textContent = "Click to browse or drop audio here";

    } catch (err) {
        alert(`Error: ${err.message}`);
    } finally {
        processBtn.disabled = false;
        loadingState.classList.add("hidden");
    }
}

async function loadMeetingHistory() {
    const listContainer = document.getElementById("historyList");
    try {
        const res = await fetch("/api/v1/meetings");
        const data = await res.json();

        if (!data.data || data.data.length === 0) {
            listContainer.innerHTML = '<p class="text-xs text-slate-400 text-center py-4">No meetings recorded yet.</p>';
            return;
        }

        listContainer.innerHTML = data.data.map(meeting => `
            <div onclick="fetchMeetingById('${meeting.id}')" 
                class="p-3 bg-slate-50 hover:bg-indigo-50 border border-slate-200 rounded-lg cursor-pointer transition text-left group">
                <p class="text-xs font-semibold text-slate-800 group-hover:text-indigo-600 truncate">${escapeHtml(meeting.title)}</p>
                <div class="flex items-center justify-between text-[11px] text-slate-400 mt-1">
                    <span>${new Date(meeting.created_at).toLocaleDateString()}</span>
                    <span>${meeting.duration_seconds ? Math.round(meeting.duration_seconds) + 's' : ''}</span>
                </div>
            </div>
        `).join("");

    } catch (err) {
        listContainer.innerHTML = '<p class="text-xs text-rose-500 text-center py-2">Failed to load history</p>';
    }
}

async function fetchMeetingById(id) {
    try {
        const res = await fetch(`/api/v1/meetings/${id}`);
        const data = await res.json();
        if (res.ok) {
            renderMeetingDetails(data.data);
        }
    } catch (err) {
        alert("Failed to retrieve meeting details.");
    }
}

function renderMeetingDetails(meeting) {
    currentMeetingId = meeting.id;
    document.getElementById("emptyState").classList.add("hidden");
    document.getElementById("resultsContainer").classList.remove("hidden");

    document.getElementById("viewTitle").textContent = meeting.title || "Untitled Meeting";
    document.getElementById("viewDate").textContent = new Date(meeting.created_at).toLocaleString();
    document.getElementById("viewDuration").textContent = meeting.duration_seconds ? `${Math.round(meeting.duration_seconds)}s` : "N/A";
    document.getElementById("viewLanguage").textContent = meeting.language.toUpperCase();

    // Summary
    document.getElementById("viewSummary").textContent = meeting.summary;

    // Key Decisions
    const decisionsContainer = document.getElementById("viewDecisions");
    if (meeting.key_decisions && meeting.key_decisions.length > 0) {
        decisionsContainer.innerHTML = meeting.key_decisions.map(d => `
            <li class="text-xs text-slate-700 flex items-start">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 mr-2 shrink-0"></span>
                <span>${escapeHtml(d)}</span>
            </li>
        `).join("");
    } else {
        decisionsContainer.innerHTML = '<li class="text-xs text-slate-400 italic">No explicit decisions recorded.</li>';
    }

    // Action Items
    const actionsContainer = document.getElementById("viewActionItems");
    if (meeting.action_items && meeting.action_items.length > 0) {
        actionsContainer.innerHTML = meeting.action_items.map(item => `
            <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-2.5 text-slate-800 font-medium">${escapeHtml(item.task)}</td>
                <td class="px-4 py-2.5">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-indigo-50 text-indigo-700">
                        ${escapeHtml(item.owner || "Unassigned")}
                    </span>
                </td>
                <td class="px-4 py-2.5">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-700">
                        ${escapeHtml(item.deadline || "Unspecified")}
                    </span>
                </td>
            </tr>
        `).join("");
    } else {
        actionsContainer.innerHTML = `
            <tr>
                <td colspan="3" class="px-4 py-3 text-center text-xs text-slate-400 italic">No actionable tasks assigned.</td>
            </tr>
        `;
    }

    // Open Questions
    const questionsContainer = document.getElementById("viewOpenQuestions");
    if (meeting.open_questions && meeting.open_questions.length > 0) {
        questionsContainer.innerHTML = meeting.open_questions.map(q => `
            <li class="text-xs text-slate-700 flex items-start">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 mr-2 shrink-0"></span>
                <span>${escapeHtml(q)}</span>
            </li>
        `).join("");
    } else {
        questionsContainer.innerHTML = '<li class="text-xs text-slate-400 italic">No open blockers or questions recorded.</li>';
    }

    // Transcript
    document.getElementById("viewTranscript").textContent = meeting.transcript;

    lucide.createIcons();
}

async function handleDeleteMeeting() {
    if (!currentMeetingId) return;
    if (!confirm("Are you sure you want to permanently delete this meeting record?")) return;

    try {
        const res = await fetch(`/api/v1/meetings/${currentMeetingId}`, { method: "DELETE" });
        if (res.ok) {
            currentMeetingId = null;
            document.getElementById("resultsContainer").classList.add("hidden");
            document.getElementById("emptyState").classList.remove("hidden");
            await loadMeetingHistory();
        }
    } catch (err) {
        alert("Failed to delete meeting.");
    }
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}