from django import forms


class UploadForm(forms.Form):
    resume = forms.FileField()
    job_description = forms.CharField(widget=forms.Textarea(attrs={"rows": 8}))
    two_column = forms.BooleanField(required=False, label="Resume has two columns")

    def clean_resume(self):
        f = self.cleaned_data["resume"]
        if not f.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Please upload a PDF file.")
        return f