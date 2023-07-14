from typing import Any, Dict
from django import forms
from django.core.exceptions import ValidationError
from User.models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(label="用户名", error_messages={
        "required":"请输入用户名",
    })
    password = forms.CharField(label="密码", widget=forms.PasswordInput())

    # clean_xxx 似乎是在自动检查完之后对字段做自定义检查.
    def clean_username(self):
        val = self.cleaned_data.get("username")
        # 检查该用户名是否存在.
        if UserProfile.objects.filter(username = val):
            return val
        else:
            raise ValidationError("该用户名不存在")
    
    # 全局钩子，自动检查完之后做全局的自定义检查.
    # 全局钩子检查出来的错误会放进form.errors.get('__all__')
    # 因为要使用auth的login函数来登录需要user实例，所以判断放在外面吧，虽然有点丑.