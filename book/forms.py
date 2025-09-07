from django import forms
from .models import Book, Tag

class BookForm(forms.ModelForm):
    new_tags = forms.CharField(
        required=False,
        help_text='カンマ区切りで新しいタグを入力できます'
    )

    class Meta:
        model = Book
        fields = ('title', 'author', 'text', 'category', 'thumbnail', 'tags')
    
    def save(self, commit=True):
        book = super().save(commit=False)
        if commit:
            book.save()
            self.save_m2m()
            #新しいタグの処理
            new_tags = self.cleaned_data.get('new_tags', '')
            if new_tags:
                for name in [t.strip() for t in new_tags.split(',') if t.strip()]:
                    tag, created = Tag.objects.get_or_create(name=name)
                    book.tags.add(tag)
        return book