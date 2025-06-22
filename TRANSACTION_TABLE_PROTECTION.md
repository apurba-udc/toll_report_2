# TRANSACTION টেবিল সুরক্ষা নীতি

## গুরুত্বপূর্ণ সতর্কতা ⚠️
**ZAKTOLL ডেটাবেসের TRANSACTION টেবিলে কোনোভাবেই পরিবর্তন করা যাবে না।**

## বর্তমান সুরক্ষা ব্যবস্থা

### ১. Model Level Protection (models.py)
```python
class Meta:
    db_table = '[TRANSACTION]'
    managed = False  # Django এই টেবিল পরিচালনা করবে না
    ordering = ['-capturedate']
    default_permissions = ()  # কোনো ডিফল্ট permission নেই
```

### ২. Custom Manager Protection
```python
class ReadOnlyManager(models.Manager):
    def create(self, **kwargs):
        raise PermissionDenied("Transaction টেবিলে কোনো নতুন ডেটা যোগ করা নিষিদ্ধ।")
    
    def update(self, **kwargs):
        raise PermissionDenied("Transaction টেবিলে কোনো আপডেট অনুমতিত নয়।")
    
    def delete(self):
        raise PermissionDenied("Transaction টেবিল থেকে কোনো ডেটা ডিলিট করা নিষিদ্ধ।")
```

### ৩. Instance Level Protection
```python
def save(self, *args, **kwargs):
    raise PermissionDenied("Transaction টেবিলে কোনো পরিবর্তন অনুমতিত নয়।")

def delete(self, *args, **kwargs):
    raise PermissionDenied("Transaction টেবিল থেকে কোনো ডেটা ডিলিট করা নিষিদ্ধ।")
```

### ৪. Admin Interface Protection (admin.py)
```python
def has_add_permission(self, request):
    return False  # নতুন transaction যোগ করা নিষিদ্ধ

def has_delete_permission(self, request, obj=None):
    return False  # transaction ডিলিট করা নিষিদ্ধ

def has_change_permission(self, request, obj=None):
    return False  # transaction পরিবর্তন করা নিষিদ্ধ
```

### ৫. Migration Protection
- `managed = False` সেটিং মাইগ্রেশনে টেবিল পরিবর্তনকে রোধ করে
- কাস্টম মাইগ্রেশন `0003_make_transaction_readonly.py` অতিরিক্ত সুরক্ষা প্রদান করে

## কি করা যাবে ✅
- Transaction ডেটা পড়া (READ)
- ফিল্টার করা
- সার্চ করা  
- রিপোর্ট তৈরি করা

## কি করা যাবে না ❌
- নতুন transaction তৈরি করা (CREATE)
- বিদ্যমান transaction আপডেট করা (UPDATE)
- Transaction ডিলিট করা (DELETE)
- টেবিল structure পরিবর্তন করা
- Migration দিয়ে টেবিল modify করা

## ডেভেলপারদের জন্য নির্দেশনা

### ১. নতুন Feature যোগ করার সময়
```python
# ভুল উদাহরণ - এটা করবেন না
transaction = Transaction.objects.get(sequence='12345')
transaction.fare = 50.00
transaction.save()  # PermissionDenied error আসবে

# সঠিক উদাহরণ - শুধু পড়ুন
transactions = Transaction.objects.filter(lane='L101')
total_fare = sum(t.fare for t in transactions if t.fare)
```

### ২. API Development
```python
# GET operations allowed
@api_view(['GET'])
def get_transactions(request):
    transactions = Transaction.objects.all()
    return Response(data)

# POST/PUT/DELETE operations না করা
# Transaction এর জন্য এই operations implement করবেন না
```

### ৩. Database Connection
```python
# Direct SQL queries এর জন্য শুধু SELECT statements
cursor.execute("SELECT * FROM [TRANSACTION] WHERE LANE = %s", [lane])

# INSERT, UPDATE, DELETE statements ব্যবহার করবেন না
```

## নিরাপত্তা চেকলিস্ট
- [ ] `managed = False` আছে কিনা
- [ ] `ReadOnlyManager` ব্যবহার হচ্ছে কিনা
- [ ] Admin permissions disabled আছে কিনা
- [ ] কোনো direct SQL write operation নেই কিনা
- [ ] API এ POST/PUT/DELETE endpoint নেই কিনা

## জরুরি যোগাযোগ
যদি কোনো কারণে Transaction টেবিলে পরিবর্তনের প্রয়োজন হয়, তাহলে:
1. Database Administrator এর সাথে যোগাযোগ করুন
2. Proper authorization নিন
3. Manual SQL script দিয়ে change করুন
4. এই application এর মাধ্যমে কোনোভাবেই পরিবর্তন করবেন না

---
**শেষ আপডেট:** ২০২৫-০১-০২  
**দায়িত্বশীল:** Database Administrator  
**ঝুঁকি স্তর:** High 🔴 