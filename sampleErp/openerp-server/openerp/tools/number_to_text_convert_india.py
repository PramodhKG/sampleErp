#-------------------------------------------------------------
# Indian
#-------------------------------------------------------------

ones = {
   0: '', 1:'one', 2:'two', 3:'three', 4:'four', 5:'five', 6:'six', 7:'seven', 8:'eight', 9:'nine',
   10:'ten', 11:'eleven', 12:'twelve', 13:'thirteen', 14:'fourteen', 15:'fifteen', 16:'sixteen',
   17:'seventeen', 18:'eighteen', 19:'nineteen', 20:'twenty',
}

tens = {
   1: 'ten', 2:'twenty', 3:'thirty',4:'forty', 5:'fifty', 6:'sixty', 7:'seventy', 8:'eighty', 9:'ninety'
}

def _100_to_text_india(chiffre):
   if chiffre in ones:
      return ones[chiffre]
   else:
      if chiffre%10>0:
         return tens[chiffre / 10]+'-'+ones[chiffre % 10]
      else:
         return tens[chiffre / 10]


def _1000_to_text_india(chiffre):
   d = _100_to_text_india(chiffre % 100)
   d2 = chiffre/100
   if d2>0:
      return ones[d2]+' hundred '+d
   else:
      return d

def _10000_to_text_india(chiffre):
   if chiffre==0:
      return 'zero'
   part1 = _1000_to_text_india(chiffre % 1000)
   part2 = (int(str(chiffre/1000)[-2:])>0 and _1000_to_text_india(int(str(chiffre/1000)[-2:]))+' thousand') or ''
   part3 = ((int(str(chiffre/100000)[-2:]))>1 and _1000_to_text_india(int(str(chiffre/100000)[-2:]))+' lakhs') or ((int(str(chiffre/100000)[-2:]))>0 and _1000_to_text_india(int(str(chiffre/100000)[-2:]))+' lakh') or ''
   part4 = ((int(str(chiffre/10000000)[-2:]))>1 and _1000_to_text_india(int(str(chiffre/10000000)[-2:]))+' crores') or ((int(str(chiffre/10000000)[-2:]))>0 and _1000_to_text_india(int(str(chiffre/10000000)[-2:]))+' crore') or ''
   if (part2 or part3 or part4) and part1:
      part1 = ' '+part1
   if (part3 or part4) and part2:
      part2 = ' '+part2
   if part4 and part3:
      part3 = ' '+part3
   return part4+part3+part2+part1


def amount_to_text_india(number, currency):
   units_number = int(number)
   units_name = currency
   if units_number > 1:
      units_name += ' '
   units = _10000_to_text_india(units_number)
   units = units_number and '%s %s' % (units_name, units.title()) or ''
   
   cents_number = int(number * 100) % 100
   cents_name = (cents_number > 1) and '& Paise' or '& Paisa'
   cents = _100_to_text_india(cents_number)
   cents = cents_number and '%s %s' % (cents_name, cents) or ''
   
   if units and cents:
      cents = ' '+cents
   return units + cents+' Only.'

def amount_format_india(number):
   l = str('%.2f' %number).split('.')[1]
   k = str(number).split('.')[0]
   t = len(k)-3
   units = ''
   for i in range(t):
      if (t+i)%2:
         units += k[i]+','
      else:
         units += k[i]
   units += k[-3:]+'.'+l[:2]
   return units

a = amount_to_text_india(236547891.98, "INR")
print a
