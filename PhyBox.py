from math import sin,cos,atan,hypot,degrees,radians,pi

def reboot(me):
    import importlib
    me=importlib.reload(me)
#========================Операции===================================
def Si(value,unit):
    units={
    "km":1000,
    "mil":1609.344,

    }
    return value*units[units]
def proection_to_vector(deltas):
    x_d,y_d=deltas[0],deltas[1]
    if x_d==0 and y_d>0: direcion=0

    elif x_d==0 and y_d<0: direcion=180

    elif y_d==0 and x_d>0: direcion=90

    elif y_d==0 and x_d<0: direcion=-90

    elif y_d > 0: direcion=degrees(atan(x_d/y_d))

    elif y_d < 0: direcion=degrees(atan(x_d/y_d))+180

    else: direcion=0

    return (direcion,hypot(x_d,y_d))

def vector_to_proection(vector):
    dir,hyp=vector[0],vector[1]
    x_d=sin(radians(dir))*hyp
    y_d=cos(radians(dir))*hyp
    return (x_d, y_d)

def sum_proections(proections):
    res=[0,0]
    for p in proections:
        res[0]+=p[0]
        res[1]+=p[1]
    return res
#===========================Законы физики получается=============================

def check_bodys_are_touch(body1,body2):
    lenght=proection_to_vector((body2.coords[0]-body1.coords[0],body2.coords[1]-body1.coords[1]))[1]
    if lenght<=body1.radius+body2.radius:
        return True
    else:
        return False

def get_Hewton_gravitation_force(body1,body2):
    G=6.674284*(10**-11)
    m1=body1.mass
    m2=body2.mass
    vec=proection_to_vector((body2.coords[0]-body1.coords[0],body2.coords[1]-body1.coords[1]))
    try:
        force=G*(m1*m2)/(vec[1]**2)
    except ZeroDivisionError:
        force=0
    return vector_to_proection((vec[0],force))

def get_Coulomb_electrostatic_force(body1,body2):
    charge1=body1.charge
    charge2=body2.charge
    e=8.85418782*(10**-12)
    k=0.25*pi*e
    charge=charge1*charge2*-1
    vec=proection_to_vector((body2.coords[0]-body1.coords[0],body2.coords[1]-body1.coords[1]))
    try:
        force=k*(charge)/(vec[1]**2)
    except ZeroDivisionError:
        force=0
    return vector_to_proection((vec[0],force))

def temp_distribution(body1,body2,time):
    dT=body2.t-body1.t
    S=min(body1.radius*(2*0.5),body2.radius*(2*0.5))
    K=min(body1.heat_conductivity,body2.heat_conductivity)
    Q=K*S*dT*time
    body1.t+=Q/(body1.mass*body1.heat_capacity)
    body2.t-=Q/(body2.mass*body2.heat_capacity)
def charge_distribution(body1,body2):
    charge1=body1.charge
    charge2=body2.charge
    V1=(body1.radius**3)*pi*(4/3)
    V2=(body2.radius**3)*pi*(4/3)
    body1.charge=(charge1+charge2)*(V1/(V1+V2))
    body2.charge=(charge1+charge2)*(V2/(V1+V2))

class World:
    def __init__(self,frequency):
        self.bodys=[]
        self.frequency=frequency
        self.replay=True

    def add(self,*args):
        for i in args:
            self.bodys.append(i)

    def log(self):
        id="Replay "+str(hash(tuple(self.bodys)))
        with open(id+".txt","a") as logfile:
            logfile.write("---\n")
            for body in self.bodys:
                logfile.write(str(body.info())+"\n")
    def tick(self,time):
        for body_num in range(len(self.bodys)):
            env=self.bodys.copy()
            env.pop(body_num)
            self.bodys[body_num].tick(env,time)

        for body in self.bodys:
            body.move(time)

    def work(self,time):
        tick_size=1/self.frequency
        print("Simulating "+str(time)+"s on "+str(self.frequency)+"Hz")
        print("Total doing "+str(int(time//tick_size))+" ticks")
        print()
        for i in range(int(time//tick_size)):
            self.tick(tick_size)
            if self.replay:
                self.log()
            print('\r'+(str(int((i+1)/int(time//tick_size)*100))+"%").ljust(4),end='')
        print()


class Body:
    def __init__(self,mass,coords,speed,t,charge,name,radius,heat_capacity,heat_conductivity):
        self.mass=mass
        self.coords=coords
        self.speed=speed
        self.t=t
        self.charge=charge
        self.name=name
        self.radius=radius
        self.heat_capacity=heat_capacity
        self.heat_conductivity=heat_conductivity # Теплопроводность, не теплоемкость!
    def info(self):
        return [self.mass,self.coords,self.speed,self.t,self.charge,self.name]

    def interact(self,body,time):
        forces=[]

        if check_bodys_are_touch(self,body):
            charge_distribution(self,body)
        forces.append(get_Hewton_gravitation_force(self,body))
        forces.append(get_Coulomb_electrostatic_force(self,body))
        return sum_proections(forces)

    def foreach_interact(self,bodys,time):
        forces=[]
        for i in bodys:
            forces.append(self.interact(i,time))
        return sum_proections(forces)


    def move(self,time):
        self.coords[0]+=self.speed[0]*time
        self.coords[1]+=self.speed[1]*time

    def tick(self,bodys,time):
        f=self.foreach_interact(bodys)
        accel=[f[0]/self.mass,f[1]/self.mass]
        self.speed[0]=self.speed[0]+accel[0]*time
        self.speed[1]=self.speed[1]+accel[1]*time
