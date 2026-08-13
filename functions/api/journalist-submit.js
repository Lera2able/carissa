const DEFAULT_ACCESS_CODE = "carissajournal2026";
const MAX_FILE_SIZE = 5 * 1024 * 1024;

const MIME_TYPES = {
  pdf: "application/pdf",
  doc: "application/msword",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function clean(value) {
  return String(value || "").trim();
}

function escapeHtml(value) {
  return clean(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}

function getExtension(filename = "") {
  const parts = filename.toLowerCase().split(".");
  return parts.length > 1 ? parts.pop() : "";
}

export async function onRequestPost(context) {
  try {
    const { request, env } = context;

    if (!env.EMAIL || typeof env.EMAIL.send !== "function") {
      return json({ success: false, error: "Email delivery is not configured yet." }, 500);
    }

    const formData = await request.formData();
    const accessCode = clean(formData.get("accessCode"));
    const expectedCode = clean(env.JOURNALIST_ACCESS_CODE) || DEFAULT_ACCESS_CODE;
    if (accessCode !== expectedCode) {
      return json({ success: false, error: "Invalid journalist code." }, 403);
    }

    const name = clean(formData.get("name"));
    const grade = clean(formData.get("grade"));
    const articleTitle = clean(formData.get("articleTitle"));
    const file = formData.get("articleFile");

    if (!name || !grade || !articleTitle || !(file instanceof File)) {
      return json({ success: false, error: "Please complete all fields and attach your article." }, 400);
    }

    if (!file.name) {
      return json({ success: false, error: "Please attach a valid article file." }, 400);
    }

    if (file.size > MAX_FILE_SIZE) {
      return json({ success: false, error: "Please keep the article file under 5MB." }, 413);
    }

    const extension = getExtension(file.name);
    if (!MIME_TYPES[extension]) {
      return json({ success: false, error: "Only PDF, DOC, and DOCX files are allowed." }, 400);
    }

    const reviewTo = clean(env.DIGEST_REVIEW_TO);
    const fromEmail = clean(env.DIGEST_FROM_EMAIL);
    const fromName = clean(env.DIGEST_FROM_NAME) || "Carissa Times";

    if (!reviewTo || !fromEmail) {
      return json({ success: false, error: "Digest email settings are incomplete." }, 500);
    }

    const sentAt = new Date().toLocaleString("en-ZA", {
      dateStyle: "long",
      timeStyle: "short",
      timeZone: "Africa/Johannesburg",
    });

    const attachmentContent = await file.arrayBuffer();
    const safeTitle = articleTitle.replace(/[^\w\s-]+/g, "").trim() || "School Digest Article";

    await env.EMAIL.send({
      to: reviewTo,
      from: { email: fromEmail, name: fromName },
      subject: `School Digest submission: ${safeTitle}`,
      replyTo: { email: fromEmail, name: fromName },
      text:
        `A new School Digest article was submitted for review.\n\n` +
        `Journalist: ${name}\n` +
        `Grade: ${grade}\n` +
        `Article title: ${articleTitle}\n` +
        `Original file: ${file.name}\n` +
        `Submitted: ${sentAt}\n`,
      html:
        `<h2>New School Digest submission</h2>` +
        `<p>A journalist has submitted a new article for review.</p>` +
        `<ul>` +
        `<li><strong>Journalist:</strong> ${escapeHtml(name)}</li>` +
        `<li><strong>Grade:</strong> ${escapeHtml(grade)}</li>` +
        `<li><strong>Article title:</strong> ${escapeHtml(articleTitle)}</li>` +
        `<li><strong>Original file:</strong> ${escapeHtml(file.name)}</li>` +
        `<li><strong>Submitted:</strong> ${escapeHtml(sentAt)}</li>` +
        `</ul>` +
        `<p>The article document is attached to this email.</p>`,
      attachments: [
        {
          content: attachmentContent,
          filename: file.name,
          type: MIME_TYPES[extension],
          disposition: "attachment",
        },
      ],
    });

    return json({ success: true });
  } catch (error) {
    return json({
      success: false,
      error: error?.message || "Could not send the article for review.",
    }, 500);
  }
}
