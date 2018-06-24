"""A collection of python stylers"""




detitle = pres['title'].split()
detitlelow = [word.lower() if word[0] != "{" else word for word in detitle]
retitle = ' '.join(detitlelow)
pres['title'] = retitle[0].capitalize() + retitle[1:]

