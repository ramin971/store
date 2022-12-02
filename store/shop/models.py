from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator,RegexValidator
from django.utils.text import slugify
from django.contrib.auth.models import User
from rest_framework.exceptions import NotAcceptable
from django.shortcuts import get_object_or_404
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
    STATUS_CHOICES = [(str(i),str(i)) for i in range(40,47)]
    value = models.CharField(max_length=2,choices=STATUS_CHOICES)
    # value = models.PositiveSmallIntegerField(validators=[MinValueValidator(39),MaxValueValidator(46)],unique=True)

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
    info = models.ManyToManyField(Info,blank=True,related_name='products')
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

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.code



class Address(models.Model):
    PROVINCE_CHOICES = (('alborz','Alborz'),('ardabil','Ardabil'),('east azerbaijan','East Azerbaijan'),('west azerbaijan','West Azerbaijan'),('bushehr','Bushehr'),('chahar mahaal and bakhtiari','Chahar Mahaal and Bakhtiari'),('fars','Fars'),('gilan','Gilan'),('golestan','Golestan'),('hamadan','Hamadan'),('hormozgan','Hormozgan'),('ilam','Ilam'),('isfahan','Isfahan'),('kerman','Kerman'),('kermanshah','Kermanshah'),('north khorasan','North Khorasan'),('razavi khorasan','Razavi Khorasan'),('south khorasan','South Khorasan'),('khuzestan','Khuzestan'),('kohgiluyeh and boyer ahmad','Kohgiluyeh and Boyer Ahmad'),('kurdistan','Kurdistan'),('lorestan','Lorestan'),('markazi','Markazi'),('mazandaran','Mazandaran'),('qazvin','Qazvin'),('qom','Qom'),('semnan','Semnan'),('sistan and baltchestan','Sistan and Baluchestan'),('tehran','Tehran'),('yazd','Yazd'),('zanjan','Zanjan'))
    province = models.CharField(max_length=30,choices=PROVINCE_CHOICES,default='tehran')
    full_address = models.TextField()


class ReceiverInformation(models.Model):
    full_name = models.CharField(max_length=50)
    national_code=models.CharField(validators=[RegexValidator(regex='^\d{10}$',message='must be 10 \
        digit',code='invalid_national_code')],max_length=10)
    phone=models.CharField(validators=[RegexValidator(regex='^[0][9][0-3][0-9]{8}$',message='phone number\
         invalid',code='invalid_phone')],max_length=11,unique=True)
    address = models.ForeignKey(Address,on_delete=models.PROTECT,related_name='receiver')
    postal_code=models.CharField(validators=[RegexValidator(regex='^\d{10}$',message='must be 10 \
        digit',code='invalid_postal_code')],max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    reciver = models.OneToOneField(ReceiverInformation,on_delete=models.SET_NULL,null=True,blank=True)
    phone=models.CharField(validators=[RegexValidator(regex='^[0][9][0-3][0-9]{8}$',message='phone number\
         invalid',code='invalid_phone')],max_length=11,unique=True)

    def __str__(self):
        return self.user.username


class Basket(models.Model):
    STATUS_CHOICES = (('queue','Queue'),('providing','Providing'),('sent','Sent'))
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='baskets')
    tracking_code = models.CharField(max_length=8,blank=True,null=True,unique=True)
    ordered_date = models.DateTimeField(null=True,blank=True)
    payment = models.BooleanField(default=False)
    receiver = models.ForeignKey(ReceiverInformation,on_delete=models.PROTECT,related_name='baskets')
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='queue')
    coupon = models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user','coupon'],name='unique_coupon')
        ]

    def __str__(self):
        return f'{self.user.username},{self.id}'

    def save(self,*args,**kwargs):
        if not self.payment:
            temp_basket = get_object_or_404(Basket,user=self.user,payment=False)
            if self !=  temp_basket:
                raise NotAcceptable('Temporary Basket is already available')
        # else:
            # self.ordered_date = datetime.datetime.now()
        super(Basket,self).save(*args,**kwargs)

class OrderItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    basket = models.ForeignKey(Basket,on_delete=models.CASCADE,related_name='order_items')
    variation = models.ForeignKey(Variation,on_delete=models.CASCADE,null=True,blank=True,related_name='order_items')

    def __str__(self):
        if self.variation:
            return f'{self.product}({self.variation.color}){self.quantity}'
        else:
            return f'{self.product}{self.quantity}'