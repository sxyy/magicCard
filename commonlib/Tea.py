# -*- encoding: utf-8 -*-
"""
The MIT License

Copyright (c) 2005 hoxide

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


QQ Crypt module.

"""
import md5,base64,rsa
from struct import pack as _pack
from struct import unpack as _unpack
from binascii import b2a_hex, a2b_hex

from random import seed
from random import randint as _randint

__all__ = ['encrypt', 'decrypt']

seed()

op = 0xffffffffL


def xor(a, b):
    a1,a2 = _unpack('>LL', a[0:8])
    b1,b2 = _unpack('>LL', b[0:8])
    r = _pack('>LL', ( a1 ^ b1) & op, ( a2 ^ b2) & op)
    return r


def code(v, k):
    n=16  #qq use 16
    delta = 0x9e3779b9L
    k = _unpack('>LLLL', k[0:16])
    y, z = _unpack('>LL', v[0:8])
    s = 0
    for i in xrange(n):
        s += delta
        y += (op &(z<<4))+ k[0] ^ z+ s ^ (op&(z>>5)) + k[1]
        y &= op
        z += (op &(y<<4))+ k[2] ^ y+ s ^ (op&(y>>5)) + k[3]
        z &= op
    r = _pack('>LL',y,z)
    return r

def encrypt(v, k):
    END_CHAR = '\0'
    FILL_N_OR = 0xF8
    vl = len(v)
    filln = ((8-(vl+2))%8) + 2
    fills = ''
    for i in xrange(filln):
        fills  += chr(_randint(0, 0xff))
    v = ( chr((filln -2)|FILL_N_OR)
          + fills
          + v
          + END_CHAR * 7)
    tr = '\0'*8
    to = '\0'*8
    r = ''
    o = '\0' * 8
    for i in xrange(0, len(v), 8):
        o = xor(v[i:i+8], tr)
        tr = xor( code(o, k), to)
        to = o
        r += tr
    return r

    
    #获取用户的加密密码       
def getTEAPass(q, p, v):
    
        #RSA 公钥
        pubkey = "F20CE00BAE5361F8FA3AE9CEFA495362FF7DA1BA628F64A347F0A8C012BF0B254A30CD92ABFFE7A6EE0DC424CB6166F8819EFA5BCCB20EDFB4AD02E412CCF579B1CA711D55B8B0B3AEB60153D5E0693A2A86F3167D7847A0CB8B00004716A9095D9BADC977CBB804DBDCBA6029A9710869A453F27DFDDF83C016D928B3CBF4C7"
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 3) 
        #MD5 密码
        p = md5.new(p).digest()

        #TEA 的KEY
        m = md5.new(p + ("%0.16X" % q).decode('hex')).digest()

        #RSA的加密结果
        n = rsa.encrypt(p, key)
        #RSA 结果的长度
        d = ("%0.4X" % len(n)).decode('hex')
            
        #RSA 加密结果
        d += n

        #salt
        d += ("%0.16X" % q).decode('hex')

        #验证码长度
        d += ("%0.4X" % len(v)).decode('hex')

        #验证码
        d += v.upper()

        #TEA 加密并Base64编码
        r = base64.b64encode(encrypt(d, m))

        #对特殊字符进行替换
        return r.replace('/', '-').replace('+', '*').replace('=', '_')
    
    
        #self.sizer.Layout()


#计算gtk的值
def getGTK(skey):
    myhash = 5381
    for i in skey:
        myhash += (myhash<<5)+ord(i)

    return  myhash & 0x7fffffff

def getBKN(skey):
    myhash = 5381
    for i in skey:
        myhash += (myhash<<5)+ord(i)
    return myhash & 0x7fffffff

