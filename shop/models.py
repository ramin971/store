from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator,RegexValidator
from django.utils.text import slugify
from django.contrib.auth.models import User
from rest_framework.exceptions import NotAcceptable,NotFound
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotAcceptable
from uuid import uuid4
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50,unique=True)
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
        return '/'.join(fullpath[::-1])
    
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
    value = models.CharField(max_length=2,choices=STATUS_CHOICES,unique=True)
    # value = models.PositiveSmallIntegerField(validators=[MinValueValidator(39),MaxValueValidator(46)],unique=True)

    def __str__(self):
        return self.value


class Info(models.Model):
    value = models.CharField(max_length=300)

    def __str__(self):
        return self.value


class Product(models.Model):
    name = models.CharField(max_length=100,unique=True,db_index=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name='products')
    description = models.TextField(blank=True,null=True)
    # discount = models.PositiveSmallIntegerField(null=True,blank=True,validators=[MinValueValidator(1),MaxValueValidator(99)])
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
    
    def __str__(self):
        return str(self.product)

class Rating(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='rates')
    rate = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),MaxValueValidator(5)])


class ProductImage(models.Model):
    image = models.ImageField(upload_to='images/%Y/')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')

    def __str__(self):
        return str(self.product)

class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='variations')
    color = models.ForeignKey(Color,on_delete=models.CASCADE,related_name='variations')
    size = models.ForeignKey(Size,on_delete=models.CASCADE,related_name='variations')
    price = models.PositiveIntegerField()
    discount = models.PositiveSmallIntegerField(null=True,blank=True,validators=[MinValueValidator(1),MaxValueValidator(99)])
    stock = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f'{self.product}({self.color}-{self.size})'

class Coupon(models.Model):
    code = models.CharField(max_length=25,unique=True)
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.code

class Province(models.Model):
    PROVINCE_CHOICES = (('alborz','Alborz'),('ardabil','Ardabil'),('east azerbaijan','East Azerbaijan'),('west azerbaijan','West Azerbaijan'),('bushehr','Bushehr'),('chahar mahaal and bakhtiari','Chahar Mahaal and Bakhtiari'),('fars','Fars'),('gilan','Gilan'),('golestan','Golestan'),('hamadan','Hamadan'),('hormozgan','Hormozgan'),('ilam','Ilam'),('isfahan','Isfahan'),('kerman','Kerman'),('kermanshah','Kermanshah'),('north khorasan','North Khorasan'),('razavi khorasan','Razavi Khorasan'),('south khorasan','South Khorasan'),('khuzestan','Khuzestan'),('kohgiluyeh and boyer ahmad','Kohgiluyeh and Boyer Ahmad'),('kurdistan','Kurdistan'),('lorestan','Lorestan'),('markazi','Markazi'),('mazandaran','Mazandaran'),('qazvin','Qazvin'),('qom','Qom'),('semnan','Semnan'),('sistan and baltchestan','Sistan and Baluchestan'),('tehran','Tehran'),('yazd','Yazd'),('zanjan','Zanjan'))
    name = models.CharField(max_length=30,choices=PROVINCE_CHOICES,default='tehran',unique=True)
    
    def __str__(self):
        return self.name

class Address(models.Model):
    province = models.ForeignKey(Province,on_delete=models.PROTECT)
    full_address = models.TextField()

    def __str__(self):
        # return str(self.province)
        return f'{self.province}/{self.full_address}'


class ReceiverInformation(models.Model):
    full_name = models.CharField(max_length=50)
    national_code=models.CharField(validators=[RegexValidator(regex='^\d{10}$',message='must be 10 \
        digit',code='invalid_national_code')],max_length=10)
    phone=models.CharField(validators=[RegexValidator(regex='^[0][9][0-3][0-9]{8}$',message='phone number\
         invalid',code='invalid_phone')],max_length=11)
    address = models.ForeignKey(Address,on_delete=models.SET_NULL,null=True,related_name='receiver')
    postal_code=models.CharField(validators=[RegexValidator(regex='^\d{10}$',message='must be 10 \
        digit',code='invalid_postal_code')],max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.full_name
    

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    receiver = models.OneToOneField(ReceiverInformation,on_delete=models.SET_NULL,null=True,blank=True)
    phone=models.CharField(validators=[RegexValidator(regex='^[0][9][0-3][0-9]{8}$',message='phone number\
         invalid',code='invalid_phone')],max_length=11,unique=True)

    def __str__(self):
        return self.user.username


class Basket(models.Model):
    STATUS_CHOICES = (('queue','Queue'),('providing','Providing'),('sent','Sent'))
    id = models.UUIDField(primary_key=True,default=uuid4,unique=True,editable=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='baskets')
    # tracking_code = models.CharField(max_length=8,blank=True,null=True,unique=True)
    tracking_code = models.UUIDField(null=True,unique=True,editable=False)
    ordered_date = models.DateTimeField(null=True,editable=False)
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

    def get_total_price(self):
        total = 0
        for order_item in self.order_items.all():
            total += order_item.get_total_product_price()
            if self.coupon:
                total = total - (self.coupon.amount * total // 100)
        return total

    def save(self,*args,**kwargs):
        if not self.payment:
            print('###payment is false')
            try:
                temp_basket = Basket.objects.get(user=self.user,payment=False)
            except Basket.DoesNotExist:
                print('######basket doesnot exist therefor create')
                return super(Basket,self).save(*args,**kwargs)
                # raise NotAcceptable('Temporary Basket is already available')
            except Basket.MultipleObjectsReturned:
                raise NotAcceptable('extra temprary basket')
            
            # temp_basket = Basket.objects.filter(user=self.user,payment=False)
            if self !=  temp_basket:
                raise NotAcceptable('Temporary Basket is already available')
            return super(Basket,self).save(*args,**kwargs)
        # else:
            # self.ordered_date = datetime.datetime.now()
        return super(Basket,self).save(*args,**kwargs)


    # def save(self,*args,**kwargs):
    #     if not self.payment:
    #         print('###payment is false')
    #         print('###user',self.user)
    #         print('###kwargs',kwargs)
    #         print('###args',args)
    #         temp_basket = Basket.objects.filter(user=self.user,payment=False)
    #         print('###temp_basket',temp_basket)
    #         if self !=  temp_basket:
    #             print('************')
    #             raise NotAcceptable('Temporary Basket is already available')
    #         print('222222222222222')
    #         super(Basket,self).save(*args,**kwargs)
    #     # else:
    #         # self.ordered_date = datetime.datetime.now()
    #     print('33333333333333333333')
    #     super(Basket,self).save(*args,**kwargs)

class OrderItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    # product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation = models.ForeignKey(Variation,on_delete=models.CASCADE,related_name='order_items')
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    basket = models.ForeignKey(Basket,on_delete=models.CASCADE,related_name='order_items')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['basket','variation'],name='unique_variation')
        ]

    def __str__(self):
        return f'{self.variation.product.name}({self.variation.color}-{self.variation.size})*{self.quantity}'

    def get_total_product_price(self):
        old_price = self.variation.price
        discount = self.variation.discount
        if discount:
            price = old_price - (discount * old_price // 100)
        else:
            # price = self.variation.price * self.quantity
            price = old_price

        return price * self.quantity

