import qrcode
img = qrcode.make('https://bengineering45.odoo.com/')
img.save('/home/bn/.local/src/tesserae/media/odoo_qr.png')
print('/home/bn/.local/src/tesserae/media/odoo_qr.png')
