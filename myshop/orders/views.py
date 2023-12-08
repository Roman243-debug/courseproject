from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from .models import OrderItem, Order
from .forms import OrderCreateForm
#from .tasks import order_created
from cart.cart import Cart
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required




def order_create(request,):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                        product=item['product'],
                                        price=item['price'],
                                        quantity=item['quantity'])
            # clear the cart
            cart.clear()
#            order_created.delay(order.id)
            # launch asynchronous task
            request.session['order_id'] = order.id
            # Перенаправить к платежу
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})


def order_created(order_id):
    """Задание по отправке уведомления по
    электронной почте при успешном создании заказа"""
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order_id}'
    message = f'Dear {order.first_name},\n\n' \
              f'Оплата прошла успешно' \
              f'Your order ID is {order.id}.'
    mail_sent = send_mail(subject,
                          message,
                          'admin@myshop.com',
                          [order.email])
    return mail_sent

def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})

