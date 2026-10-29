from django import forms

MAX_UPLOAD_MB = 5
ALLOWED_EXTENSIONS = (".pdf", ".docx")


class UploadForm(forms.Form):
    resume = forms.FileField()
    job_description = forms.CharField(widget=forms.Textarea(attrs={"rows": 8}))
    two_column = forms.BooleanField(required=False, label="Resume has two columns")

    def clean_resume(self):
        f = self.cleaned_data["resume"]
        name = f.name.lower()
        if not name.endswith(ALLOWED_EXTENSIONS):
            raise forms.ValidationError("Please upload a PDF or DOCX file.")
        if f.size > MAX_UPLOAD_MB * 1024 * 1024:
            raise forms.ValidationError(f"File is too large. The limit is {MAX_UPLOAD_MB} MB.")

        # Check the file's first bytes, not just its name. A DOCX is a zip file ("PK").
        head = f.read(4)
        f.seek(0)
        expected = b"%PDF" if name.endswith(".pdf") else b"PK\x03\x04"
        if not head.startswith(expected):
            raise forms.ValidationError("This file is not a valid PDF or DOCX document.")
        return f