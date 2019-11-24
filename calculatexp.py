import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

print("Getting xps from messages")
url = "https://slack.com/api/channels.history"
querystring = {"token":"{your token}","channel":"CJWDYLS2Z","pretty":"1"}
headers = {
    'User-Agent': "PostmanRuntime/7.17.1",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "{postman-token}",
    'Host': "slack.com",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

xp = pd.DataFrame(columns = ["id", "xp_value"])
name = pd.DataFrame(columns = ["id", "real_name"])

response = requests.request("GET", url, headers=headers, params=querystring)
ress = response.json()

for i in range(len(ress["messages"])):
    text = ress["messages"][i]["text"]
    #print(text)
        #find for xp
    index = text.find('xp ')
        #conditions if not found
    if(index == -1):
        index = text.find('XP ')
    if(index == -1):
        continue
        
        #get xp value
    try:
        xp_val = int(text[: index].strip(' ')[-2:])
        
    
    except:
        continue
    
    
    for t in text.split("@")[1:]:
        id = t.split(">")[:-1]
        for i in id:
            xp = xp.append(pd.Series([i, xp_val], index = xp.columns), ignore_index = True)

print("Getting Names of users")       

url = "https://slack.com/api/users.list"
querystring = {"token":"{your-token}","pretty":"1"}
headers = {
    'User-Agent': "PostmanRuntime/7.17.1",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "{postman token}",
    'Host': "slack.com",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response1 = requests.request("GET", url, headers=headers, params=querystring)
res = response1.json()

for i in range(len(res["members"])):
    info = res["members"][i]
    n = info["profile"]["real_name"]
    id = info["id"]
    name = name.append(pd.Series([id, n], index = name.columns), ignore_index = True)

result = pd.DataFrame(columns=['id', 'real_name', 'xp'])

name.sort_values(by='id', ascending=[1], inplace=True)
xp.sort_values(by='id', ascending=[1], inplace=True)

print("Mapping xps to users")

for index, rowx in xp.iterrows():
   for index, rown in name[rowx['id']==name['id']].iterrows():
       result = result.append(pd.Series([rown['id'], rown['real_name'], rowx['xp_value']], index=result.columns), ignore_index=True)

print("Calculating total xps of each students")

result = result.groupby(['id','real_name']).sum().reset_index()
result = result.sort_values(by = 'xp', ascending = False).reset_index(drop = True)

x = result['xp']
y = result['real_name']
colors = cm.hsv(x / float(max(x)))
plot = plt.scatter(x, x, c = x, cmap = 'hsv')
plt.clf()

fig= plt.figure(figsize=(10,4))
axes= fig.add_axes([0.1,0.1,0.8,4])
axes.set_ylim([len(y), 0])
plt.xticks(np.arange(0, 100, 10))
axes.barh(y, x, color = colors)
#axes.barh(result['real_name'], result['xp'], align = 'center')
plt.xlabel("Total xps")
plt.ylabel("Name")
plt.colorbar(plot)

rects = axes.patches

# For each bar: Place a label
for rect in rects:
    # Get X and Y placement of label from rect.
    x_value = rect.get_width()
    y_value = rect.get_y() + rect.get_height() / 2

    # Number of points between bar and label. Change to your liking.
    space = 5
    # Vertical alignment for positive values
    ha = 'left'

    # If value of bar is negative: Place label left of bar
    if x_value < 0:
        # Invert space to place label to the left
        space *= -1
        # Horizontally align label at right
        ha = 'right'

    # Use X value as label and format number with one decimal place
    label = "{:.1f}".format(x_value)

    # Create annotation
    plt.annotate(
        label,                      # Use `label` as label
        (x_value, y_value),         # Place label at end of the bar
        xytext=(space, 0),          # Horizontally shift label by `space`
        textcoords="offset points", # Interpret `xytext` as offset in points
        va='center',                # Vertically center label
        ha=ha)                      # Horizontally align label differently for
                                    # positive and negative values.
#plt.show()
print("Saving graph to image")

fig.savefig('xpreport.jpg', bbox_inches = 'tight')

print("Mailing")

import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
  
fromaddr = "cee300asu@gmail.com"
toaddr = ["Fall_20.2wm5iqal96jxq5ht@u.box.com", "thakkarsamip@gmail.com"]
 
for i in toaddr:
    msg = MIMEMultipart()
    msg['From'] = fromaddr 
    msg['To'] = i
    msg['Subject'] = "Mail with attachment"
    body = "PFA"
    msg.attach(MIMEText(body, 'plain')) 
    filename = "xpreport.jpg"
    
    attachment = open("xpreport.jpg", "rb") 
    p = MIMEBase('application', 'octet-stream') 
    p.set_payload((attachment).read()) 
    encoders.encode_base64(p) 
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    msg.attach(p) 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login(fromaddr, "thomasseager") 
    text = msg.as_string() 
    s.sendmail(fromaddr, i, text) 
    s.quit() 
print("Check your mails!!!!")
