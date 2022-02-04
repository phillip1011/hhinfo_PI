import subprocess


def get_process(cmd):
    try:
        item = subprocess.check_output(cmd, shell=True)	
        return item
    except:
        return ''
def get_serial_name(usb_names):

    cmd = "sudo dmesg |grep 'converter now attached to ttyUSB' |grep"
    for usb_name in usb_names:
        cmd  = cmd + " '" + usb_name + "'"
    print (cmd)
    res = get_process(cmd)
    #res=str(res)
    #print(type(res))
    items = str(res).split("\\n")
    #print(len(items))
    last_time = 0.0
    serial_name ="ttyAMA0"
    for item in items:
        #print(item)
        l1 = item.find('[')
        l2 = item.find(']') 
        #print(l1,l2)
        if l1 > -1 and l2 > 0 :
            #print(l1,l2,len(item) )
            time_sn = item[l1+1:l2-1]
            this_time = float(time_sn)
            #print(this_time,last_time)
            if (this_time > last_time):
                last_time = this_time
                
                l3 = item.find('ttyUSB')
                if (l3 >0):
                    #print (l3)
                    serial_name = item[l3:l3+7]
                    #print('name=',serial_name)
    return serial_name
#usb_names =['usb 1-1.1','usb 1-1.2']
#ss = get_serial_name(usb_names)
#print (ss)
