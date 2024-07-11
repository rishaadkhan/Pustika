from . models import books,UserProfile
from django import forms

class sellbookform(forms.ModelForm):
    CATEGORY_CHOICES = [('Engineering','Engineering'),('Fiction', 'Fiction'),('Non-Fiction', 'Non-Fiction'),('Children', 'Children'),('Science', 'Science'),('Technology', 'Technology')]
    class Meta:
        model = books
        fields = [
            'book_name',
            'category',
            'price',
            'image',
            'pickuplocation',
            'sellername',
        ]
    book_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    price = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    sellername = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )

    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file'
        })
    )

    pickuplocation = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )    


#user profle form
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields:fields = ['full_name','address', 'address2', 'city', 'state', 'zip_code', 'phone_number']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['address2'].widget.attrs.update({'class': 'form-control'})
        self.fields['city'].widget.attrs.update({'class': 'form-control'})
        self.fields['state'].widget.attrs.update({'class': 'form-control'})
        self.fields['zip_code'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})