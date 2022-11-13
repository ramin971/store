from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.utils.text import slugify
from django.contrib.auth.models import User
from rest_framework.exceptions import NotAcceptable

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='child')

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['slug','parent'],name='unique_slug_category')
        ]

    def __str__(self):
        fullpath = [self.name]
        parent = self.parent
        while parent:
            fullpath.append(parent.name)
            parent = parent.parent
        return '-> '.join(fullpath[::-1])
    
    def save(self,*args,**kwargs):
        self.slug = slugify(self.name)
        if self == self.parent:
            raise NotAcceptable('Not Acceptable')        
        super(Category,self).save(*args,**kwargs)
        


class Color(models.Model):
    value = models.CharField(max_length=30,unique=True)

    def __str__(self):
        return self.value

class Size(models.Model):
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(39),MaxValueValidator(46)],unique=True)

    def __str__(self):
        return self.value


class Info(models.Model):
    value = models.CharField(max_length=300)

    def __str__(self):
        return self.value


class Product(models.Model):
    name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name='products')
    description = models.TextField(blank=True,null=True)
    discount = models.PositiveSmallIntegerField(null=True,blank=True,validators=[MinValueValidator(1),MaxValueValidator(99)])
    size = models.ManyToManyField(Size,related_name='products')
    info = models.ManyToManyField(Info,related_name='products')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    
    def save(self,*args,**kwargs):
        self.slug = slugify(self.name)
        super(Product,self).save(*args,**kwargs)

class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comments')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='comments')
    text = models.TextField()

    class Meta:
        ordering = ('-id',)

class Rating(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='rates')
    rate = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),MinValueValidator(5)])


class ProductImage(models.Model):
    image = models.ImageField(upload_to='images/%Y/')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')

    def __str__(self):
        return str(self.product)

class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='variations')
    color = models.ManyToManyField(Color,related_name='variations')
    price = models.PositiveIntegerField()
    discount = models.PositiveSmallIntegerField(null=True,blank=True,validators=[MinValueValidator(1),MaxValueValidator(99)])
    stock = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.product)


