#!/usr/bin/env python
#-*- coding:utf-8 -*-

import cv2.cv as cv
from math import pi,atan2,sqrt
from numpy import matrix
from time import time, sleep

den = 2

class CubeCapture(object):
    def __init__(self, without_robot=False):
        super(CubeCapture, self).__init__()
        
        self.capture = cv.CreateCameraCapture( 0 )
        cv.NamedWindow( "Fig", 1 )
        frame = cv.QueryFrame( self.capture )
        if not frame:
            raise IOError, "Couldn't find camera."
        S1, S2 = cv.GetSize(frame)
        
        self.sg = cv.CreateImage((S1/den,S2/den), 8, 3 )
        self.sgc = cv.CreateImage((S1/den,S2/den), 8, 3 )
        self.hsv = cv.CreateImage((S1/den,S2/den), 8, 3 )
        self.dst = cv.CreateImage((S1/den,S2/den), 8, 1 )
        self.d = cv.CreateImage((S1/den,S2/den), cv.IPL_DEPTH_16S, 1 )
        self.d2 = cv.CreateImage((S1/den,S2/den), 8, 1 )
        self.b = cv.CreateImage((S1/den,S2/den), 8, 1 )
        self.b4 = cv.CreateImage((S1/den,S2/den), 8, 1 )
        self.both = cv.CreateImage((S1/den,S2/den), 8, 1 )
        self.harr = cv.CreateImage((S1/den,S2/den), 32, 1 )
        self.W, self.H = S1/den, S2/den
        self.lastdetected = 0
        self.THR = 100
        self.dects = 50 #ideal number of number of lines detections
        
        self.hue = cv.CreateImage((S1/den,S2/den), 8, 1 )
        self.sat = cv.CreateImage((S1/den,S2/den), 8, 1 )
        self.val = cv.CreateImage((S1/den,S2/den), 8, 1 )
        
        #stores the coordinates that make up the face. in order: p,p1,p3,p2 (i.e.) counterclockwise winding
        self.prevface = [(0,0),(5,0),(0,5)]
        self.dodetection = True
        
        self.onlyBlackCubes = False

        self.looping = True
        self.color = [] # for captured one face
        self.interrupt = False
        # robot
        self.without_robot = without_robot

    def grid(self, p):
        """Return the nearest point with integer coordinates to p."""
        return int(round(p[0])), int(round(p[1]))


    def intersect_seg(self, x1,x2,x3,x4,y1,y2,y3,y4):
        den= (y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)
        if abs(den)<0.1: return (False, (0,0),(0,0))
        ua=(x4-x3)*(y1-y3)-(y4-y3)*(x1-x3)
        ub=(x2-x1)*(y1-y3)-(y2-y1)*(x1-x3)    
        ua=ua/den
        ub=ub/den
        x=x1+ua*(x2-x1)
        y=y1+ua*(y2-y1)
        return (True,(ua,ub),(x,y))

    def ptdst(self, p1,p2):
        return sqrt((p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1]))

    def ptdstw(self, p1,p2):
        #return sqrt((p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1]))

        #test if hue is reliable measurement
        if p1[1]<100 or p2[1]<100:
            #hue measurement will be unreliable. Probably white stickers are present
            #leave this until end
            return 300.0+abs(p1[0]-p2[0])
        else:
            return abs(p1[0]-p2[0])


    def ptdst3(self, p1,p2):
        dist=sqrt((p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1])+(p1[2]-p2[2])*(p1[2]-p2[2]))
        if (p1[0]>245 and p1[1]>245 and p1[2]>245):
        #the sticker could potentially be washed out. Lets leave it to the end
            dist=dist+300.0
        return dist

    def compfaces(self, f1,f2):
        totd=0
        for p1 in f1:
            mind=10000
            for p2 in f2:
                d=self.ptdst(p1,p2)
                if d<mind:
                    mind=d
            totd += mind
        return totd/4

    def avg(self, p1,p2):
        return (0.5*p1[0]+0.5*p2[0], 0.5*p2[1]+0.5*p2[1])

    def areclose(self, t1,t2,t):
        #is t1 close to t2 within t?
        return abs(t1[0]-t2[0])<t and abs(t1[1]-t2[1])<t

    def winded(self, p1,p2,p3,p4):
        #return the pts in correct order based on quadrants
        avg = (0.25*(p1[0]+p2[0]+p3[0]+p4[0]),0.25*(p1[1]+p2[1]+p3[1]+p4[1]))
        ps = [(atan2(p[1]-avg[1], p[0]-avg[0]), p) for p in [p1,p2,p3,p4]]
        ps.sort(reverse=True)
        return [p[1] for p in ps]

    #return tuple of neighbors given face and sticker indeces
    def neighbors(self, f,s):
        if f==0 and s==0: return ((1,2),(4,0))
        if f==0 and s==1: return ((4,3),)
        if f==0 and s==2: return ((4,6),(3,0))
        if f==0 and s==3: return ((1,5),)
        if f==0 and s==5: return ((3,3),)
        if f==0 and s==6: return ((1,8),(5,2))
        if f==0 and s==7: return ((5,5),)
        if f==0 and s==8: return ((3,6),(5,8))
        
        if f==1 and s==0: return ((2,2),(4,2))
        if f==1 and s==1: return ((4,1),)
        if f==1 and s==2: return ((4,0),(0,0))
        if f==1 and s==3: return ((2,5),)
        if f==1 and s==5: return ((0,3),)
        if f==1 and s==6: return ((2,8),(5,0))
        if f==1 and s==7: return ((5,1),)
        if f==1 and s==8: return ((0,6),(5,2))
        
        if f==2 and s==0: return ((4,8),(3,2))
        if f==2 and s==1: return ((4,5),)
        if f==2 and s==2: return ((4,2),(1,0))
        if f==2 and s==3: return ((3,5),)
        if f==2 and s==5: return ((1,3),)
        if f==2 and s==6: return ((3,8),(5,6))
        if f==2 and s==7: return ((5,3),)
        if f==2 and s==8: return ((1,6),(5,0))
        
        if f==3 and s==0: return ((4,6),(0,2))
        if f==3 and s==1: return ((4,7),)
        if f==3 and s==2: return ((4,8),(2,0))
        if f==3 and s==3: return ((0,5),)
        if f==3 and s==5: return ((2,3),)
        if f==3 and s==6: return ((0,8),(5,8))
        if f==3 and s==7: return ((5,7),)
        if f==3 and s==8: return ((2,6),(5,6))
        
        if f==4 and s==0: return ((1,2),(0,0))
        if f==4 and s==1: return ((1,1),)
        if f==4 and s==2: return ((1,0),(2,2))
        if f==4 and s==3: return ((0,1),)
        if f==4 and s==5: return ((2,1),)
        if f==4 and s==6: return ((0,2),(3,0))
        if f==4 and s==7: return ((3,1),)
        if f==4 and s==8: return ((3,2),(2,0))
        
        if f==5 and s==0: return ((1,6),(2,8))
        if f==5 and s==1: return ((1,7),)
        if f==5 and s==2: return ((1,8),(0,6))
        if f==5 and s==3: return ((2,7),)
        if f==5 and s==5: return ((0,7),)
        if f==5 and s==6: return ((2,6),(3,8))
        if f==5 and s==7: return ((3,7),)
        if f==5 and s==8: return ((3,6),(0,8))
        
    def processColors(self, useRGB=True):
        #assign all colors
        bestj=0
        besti=0
        bestcon=0
        matchesto=0
        bestd=10001
        taken=[0 for i in range(6)]
        done=0
        opposite={0:2, 1:3, 2:0, 3:1, 4:5, 5:4} #dict of opposite faces
        #possibilities for each face
        poss={}
        for j,f in enumerate(self.hsvs):
            for i,s in enumerate(f):
                poss[j,i]=range(6)
                
        #we are looping different arrays based on the useRGB flag
        toloop=self.hsvs
        if useRGB: toloop=self.colors
        
        while done<8*6:
            bestd=10000
            forced=False
            for j,f in enumerate(toloop):
                for i,s in enumerate(f):
                    if i!=4 and self.assigned[j][i]==-1 and (not forced):
                        #this is a non-center sticker.
                        #find the closest center
                        considered=0
                        for k in poss[j,i]:
                            #all colors for this center were already assigned
                            if taken[k]<8:
                                
                                #use Euclidean in RGB space or more elaborate
                                #distance metric for Hue Saturation
                                if useRGB:
                                    dist = self.ptdst3(s, toloop[k][4])
                                else:
                                    dist = self.ptdstw(s, toloop[k][4])
                                    
                                considered+=1
                                if dist<bestd:
                                    bestd=dist
                                    bestj=j
                                    besti=i
                                    matchesto=k
                        #IDEA: ADD PENALTY IF 2ND CLOSEST MATCH IS CLOSE TO FIRST
                        #i.e. we are uncertain about it
    
                        if besti==i and bestj==j: bestcon=considered
                        if considered==1:
                            #this sticker is forced! Terminate search 
                            #for better matches
                            forced=True
                            print 'sticker',(i,j),'had color forced!'


            #assign it
            done=done+1
            #print matchesto,bestd
            self.assigned[bestj][besti]=matchesto
            print bestcon
            
            op= opposite[matchesto] #get the opposite side
            #remove this possibility from neighboring stickers
            #since we cant have red-red edges for example
            #also corners have 2 neighbors. Also remove possibilities
            #of edge/corners made up of opposite sides
            ns=self.neighbors(bestj,besti)
            for neighbor in ns:
                p=poss[neighbor]
                if matchesto in p: p.remove(matchesto)
                if op in p: p.remove(op)
                
            taken[matchesto]+=1
    
        self.didassignments=True
        
    def run(self, next_face):
        succ=0 #number of frames in a row that we were successful in finding the outline
        tracking=0
        win_size=5
        flags=0
        detected=0
        
        grey = cv.CreateImage ((self.W,self.H), 8, 1)
        prev_grey = cv.CreateImage ((self.W,self.H), 8, 1)
        pyramid = cv.CreateImage ((self.W,self.H), 8, 1)
        prev_pyramid = cv.CreateImage ((self.W,self.H), 8, 1)
    
        ff= cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1,1, shear=0, thickness=1, lineType=8)
        
        counter=0 #global iteration counter
        undetectednum=100
        stage=1 #1: learning colors
        extract=True
        selected=0
        self.colors=[[] for i in range(6)]
        self.hsvs=[[] for i in range(6)]
        self.assigned=[[-1 for i in range(9)] for j in range(6)]
        for i in range(6): # set center cube correctly
            self.assigned[i][4]=i

        self.didassignments=False
        #orange green red blue yellow white. Used only for visualization purposes
        mycols=[(0,127,255), (20,240,20), (0,0,255), (200,0,0), (0,255,255), (255,255,255)]
        
        while self.looping:
            frame = cv.QueryFrame( self.capture )
            if not frame:
                cv.WaitKey(0)
                break
            
            cv.Resize( frame, self.sg)

            #cv.EqualizeHist(val, val)
            #cv.Merge(hue,sat,val,None,sg2)
            #cv.CvtColor(sg2,sg,cv.CV_HSV2RGB)
            cv.Copy(self.sg, self.sgc)
        
            cv.CvtColor (self.sg, grey, cv.CV_RGB2GRAY)
            
            #cv.EqualizeHist(grey,grey)
            
            #tracking mode
            if tracking>0:
                
                detected=2
                #compute optical flow
                features, status, track_error = cv.CalcOpticalFlowPyrLK (
                    prev_grey, grey, prev_pyramid, pyramid,
                    features,
                    (win_size, win_size), 3,
                    (cv.CV_TERMCRIT_ITER|cv.CV_TERMCRIT_EPS, 20, 0.03),
                    flags)
                # set back the points we keep
                features = [ p for (st,p) in zip(status, features) if st]
                if len(features)<4: 
                    tracking= 0 #we lost it, restart search
                else:
                    #make sure that in addition the distances are consistent
                    ds1=self.ptdst(features[0], features[1])
                    ds2=self.ptdst(features[2], features[3])
                    if max(ds1,ds2)/min(ds1,ds2)>1.4: tracking=0
                
                    ds3=self.ptdst(features[0], features[2])
                    ds4=self.ptdst(features[1], features[3])
                    if max(ds3,ds4)/min(ds3,ds4)>1.4: tracking=0
                    
                    if ds1< 10 or ds2<10 or ds3<10 or ds4<10: tracking=0
                    if tracking==0: detected=0
                    
            #detection mode
            if tracking==0:
                detected=0
                cv.Smooth(grey,self.dst,cv.CV_GAUSSIAN, 3)
                cv.Laplace(self.dst,self.d)
                cv.CmpS(self.d,8,self.d2,cv.CV_CMP_GT)
                
                if self.onlyBlackCubes:
                    #can also detect on black lines for improved robustness
                    cv.CmpS(grey,100,self.b,cv.CV_CMP_LT)
                    cv.And(b,self.d2,self.d2)
                    
                #these weights should be adaptive. We should always detect 100 lines
                if self.lastdetected>self.dects: self.THR=self.THR+1
                if self.lastdetected<self.dects: self.THR=max(2,self.THR-1)
                li= cv.HoughLines2(self.d2, cv.CreateMemStorage(), cv.CV_HOUGH_PROBABILISTIC, 1, 3.1415926/45, self.THR, 10, 5)
                
                #store angles for later
                angs=[]
                for (p1, p2) in li: 
                    #cv.Line(sg,p1,p2,(0,255,0))
                    a = atan2(p2[1]-p1[1],p2[0]-p1[0])
                    if a<0:a+=pi
                    angs.append(a)
                    
                #lets look for lines that share a common end point
                t=10
                totry=[]
                for i in range(len(li)):
                    p1,p2=li[i]
                    for j in range(i+1,len(li)):
                        q1,q2=li[j]
                        
                        #test lengths are approximately consistent
                        dd1= sqrt((p2[0]-p1[0])*(p2[0]-p1[0])+(p2[1]-p1[1])*(p2[1]-p1[1]))
                        dd2= sqrt((q2[0]-q1[0])*(q2[0]-q1[0])+(q2[1]-q1[1])*(q2[1]-q1[1]))
                        if max(dd1,dd2)/min(dd1,dd2)>1.3: continue
                        
                        matched=0
                        if self.areclose(p1,q2,t): 
                            IT=(self.avg(p1,q2), p2, q1,dd1)
                            matched=matched+1
                        if self.areclose(p2,q2,t): 
                            IT=(self.avg(p2,q2), p1, q1,dd1)
                            matched=matched+1
                        if self.areclose(p1,q1,t): 
                            IT=(self.avg(p1,q1), p2, q2,dd1)
                            matched=matched+1
                        if self.areclose(p2,q1,t): 
                            IT=(self.avg(p2,q1), q2, p1,dd1)
                            matched=matched+1
                            
                        if matched==0:
                            #not touching at corner... try also inner grid segments hypothesis?
                            p1=(float(p1[0]),float(p1[1]))
                            p2=(float(p2[0]),float(p2[1]))
                            q1=(float(q1[0]),float(q1[1]))
                            q2=(float(q2[0]),float(q2[1]))
                            success,(ua,ub),(x,y)=\
                                self.intersect_seg(p1[0],p2[0],q1[0],q2[0],p1[1],p2[1],q1[1],q2[1])
                            if success and ua>0 and ua<1 and ub>0 and ub<1:
                                #if they intersect
                                #cv.Line(sg, p1, p2, (255,255,255))
                                ok1=0
                                ok2=0
                                if abs(ua-1.0/3)<0.05:ok1=1
                                if abs(ua-2.0/3)<0.05:ok1=2
                                if abs(ub-1.0/3)<0.05:ok2=1
                                if abs(ub-2.0/3)<0.05:ok2=2
                                if ok1>0 and ok2>0:
                                    #ok these are inner lines of grid
                                    #flip if necessary
                                    if ok1==2: p1,p2=p2,p1
                                    if ok2==2: q1,q2=q2,q1
                                    
                                    #both lines now go from p1->p2, q1->q2 and 
                                    #intersect at 1/3
                                    #calculate IT
                                    z1=(q1[0]+2.0/3*(p2[0]-p1[0]),q1[1]+2.0/3*(p2[1]-p1[1]))
                                    z2=(p1[0]+2.0/3*(q2[0]-q1[0]),p1[1]+2.0/3*(q2[1]-q1[1]))
                                    z=(p1[0]-1.0/3*(q2[0]-q1[0]),p1[1]-1.0/3*(q2[1]-q1[1]))
                                    IT=(z,z1,z2,dd1)
                                    matched=1
                                    
                        #only single one matched!! Could be corner
                        if matched==1:
                            
                            #also test angle
                            a1 = atan2(p2[1]-p1[1],p2[0]-p1[0])
                            a2 = atan2(q2[1]-q1[1],q2[0]-q1[0])
                            if a1<0:a1+=pi
                            if a2<0:a2+=pi
                            ang=abs(abs(a2-a1)-pi/2)
                            if ang < 0.5:
                                totry.append(IT)
                                #cv.Circle(sg, IT[0], 5, (255,255,255))
                                
                                
                #now check if any points in totry are consistent!
                #t=4
                res=[]
                for i in range(len(totry)):
                    
                    p,p1,p2,dd=totry[i]
                    a1 = atan2(p1[1]-p[1],p1[0]-p[0])
                    a2 = atan2(p2[1]-p[1],p2[0]-p[0])
                    if a1<0:a1+=pi
                    if a2<0:a2+=pi
                    dd=1.7*dd
                    evidence=0
                    totallines=0
                    
                    #cv.Line(sg,p,p2,(0,255,0))
                    #cv.Line(sg,p,p1,(0,255,0))
    
                    #affine transform to local coords
                    A = matrix([[p2[0]-p[0],p1[0]-p[0],p[0]],[p2[1]-p[1],p1[1]-p[1],p[1]],[0,0,1]])
                    Ainv= A.I
                    
                    v=matrix([[p1[0]],[p1[1]],[1]])
                    
                    #check likelihood of this coordinate system. iterate all lines
                    #and see how many align with grid
                    for j in range(len(li)):
                        
                        #test angle consistency with either one of the two angles
                        a = angs[j]
                        ang1=abs(abs(a-a1)-pi/2)
                        ang2=abs(abs(a-a2)-pi/2)
                        if ang1 > 0.1 and ang2>0.1: continue
                        
                        #test position consistency.
                        q1,q2= li[j]
                        qwe=0.06
                        
                        #test one endpoint
                        v=matrix([[q1[0]],[q1[1]],[1]])
                        vp=Ainv*v; #project it
                        if vp[0,0] > 1.1 or vp[0,0]<-0.1: continue
                        if vp[1,0] > 1.1 or vp[1,0]<-0.1: continue
                        if abs(vp[0,0]-1/3.0)>qwe and abs(vp[0,0]-2/3.0)>qwe and \
                                abs(vp[1,0]-1/3.0)>qwe and abs(vp[1,0]-2/3.0)>qwe: continue
                        
                        #the other end point
                        v=matrix([[q2[0]],[q2[1]],[1]])
                        vp=Ainv*v;
                        if vp[0,0] > 1.1 or vp[0,0]<-0.1: continue
                        if vp[1,0] > 1.1 or vp[1,0]<-0.1: continue
                        if abs(vp[0,0]-1/3.0)>qwe and abs(vp[0,0]-2/3.0)>qwe and \
                                abs(vp[1,0]-1/3.0)>qwe and abs(vp[1,0]-2/3.0)>qwe: continue
                        
                        #cv.Circle(sg, q1, 3, (255,255,0))
                        #cv.Circle(sg, q2, 3, (255,255,0))
                        #cv.Line(sg,q1,q2,(0,255,255))
                        evidence+=1
    
                    #print evidence
                    res.append((evidence, (p,p1,p2)))
        
                minch=10000
                res.sort(reverse=True)
                #print [a[0] for a in res]
                if len(res)>0:
                    minps=[]
                    pt=[]
                    #among good observations find best one that fits with last one
                    for i in range(len(res)):
                        if res[i][0]>0.05*self.dects:
                            #OK WE HAVE GRID
                            p,p1,p2=res[i][1]
                            p3= (p2[0]+p1[0]-p[0], p2[1]+p1[1]-p[1])
                            
                            #cv.Line(sg,p,p1,(0,255,0),2)
                            #cv.Line(sg,p,p2,(0,255,0),2)
                            #cv.Line(sg,p2,p3,(0,255,0),2)
                            #cv.Line(sg,p3,p1,(0,255,0),2)
                            #cen=(0.5*p2[0]+0.5*p1[0],0.5*p2[1]+0.5*p1[1])
                            #cv.Circle(sg, cen, 20, (0,0,255),5)
                            #cv.Line(sg, (0,cen[1]), (320,cen[1]),(0,255,0),2)
                            #cv.Line(sg, (cen[0],0), (cen[0],240), (0,255,0),2)
                            
                            w=[p,p1,p2,p3]
                            p3= (self.prevface[2][0]+self.prevface[1][0]-self.prevface[0][0], 
                                 self.prevface[2][1]+self.prevface[1][1]-self.prevface[0][1])
                            tc= (self.prevface[0],self.prevface[1],self.prevface[2],p3)
                            ch=self.compfaces(w,tc) 
                            if ch<minch:
                                minch=ch
                                minps= (p,p1,p2)
                                
                    if len(minps)>0:
                        self.prevface=minps
                        #print minch
                        
                        if minch<10:
                            #good enough!
                            succ+=1
                            pt=self.prevface
                            detected=1
        
                    else:
                        succ=0
    
                    #we matched a few times same grid
                    #coincidence? I think NOT!!! Init LK tracker
                    if succ>2 and 1:
                        #initialize features for LK
                        pt=[]
                        for i in [1.0/3, 2.0/3]:
                            for j in [1.0/3, 2.0/3]:
                                pt.append((p0[0]+i*v1[0]+j*v2[0], p0[1]+i*v1[1]+j*v2[1]))
        
                        #refine points slightly
                        #features = cv.FindCornerSubPix (
                        #grey,
                        #pt,
                        #(win_size, win_size),  (-1, -1),
                        #(cv.CV_TERMCRIT_ITER | cv.CV_TERMCRIT_EPS,
                        #20, 0.03))
                        features=pt
                        tracking=1
                        succ=0
                        
            else:
                #we are in tracking mode, we need to fill in pt[] array
                #calculate the pt array for drawing from features
                #for p in features:
                #    cv.Circle(sg, p, 3, (255,255,255),-1)
                p=features[0]
                p1=features[1]
                p2=features[2]
                
                print p
                print p1
                print p2
                
                v1=(p1[0]-p[0],p1[1]-p[1])
                v2=(p2[0]-p[0],p2[1]-p[1])
                
                pt=[(p[0]-v1[0]-v2[0], p[1]-v1[1]-v2[1]),
                    (p[0]+2*v2[0]-v1[0], p[1]+2*v2[1]-v1[1]),
                    (p[0]+2*v1[0]-v2[0], p[1]+2*v1[1]-v2[1])]
                
                self.prevface=[pt[0],pt[1],pt[2]]
                
            #use pt[] array to do drawing
            if (detected or undetectednum<1) and self.dodetection:
                #undetectednum 'fills in' a few detection to make
                #things look smoother in case we fall out one frame
                #for some reason
                if not detected: 
                    undetectednum+=1
                    pt=lastpt
                if detected: 
                    undetectednum=0
                    lastpt=pt
                    
                    #print pt
                new_pt = []
                for npt in pt:
                    new_pt.append((int(round(npt[0])), int(round(npt[1]))))
                    
                pt = new_pt
                print pt
                
                #~ pt = [p = (round(p[0]), round(p[1])) for p in pt]
                #~ pt = [p = (round(p[0]), round(p[1])) for p in pt]
                #~ for p in pt:
                  #~ print p
                  #~ return int(round(p[0])), int(round(p[1]))
                  #~ [p = (round(p[0]), round(p[1])) for p in pt]
                  #~ print "new"
                  #~ print p
                
                #extract the colors
                #convert to HSV
                cv.CvtColor(self.sgc, self.hsv, cv.CV_RGB2HSV)
                cv.Split(self.hsv, self.hue, self.sat, self.val, None)
                
                #do the drawing. pt array should store p,p1,p2
                p3= (pt[2][0]+pt[1][0]-pt[0][0], pt[2][1]+pt[1][1]-pt[0][1])
                cv.Line(self.sg,pt[0],pt[1],(0,255,0),2)
                cv.Line(self.sg,pt[1],p3,(0,255,0),2)
                cv.Line(self.sg,p3,pt[2],(0,255,0),2)
                cv.Line(self.sg,pt[2],pt[0],(0,255,0),2)
                
                #first sort the points so that 0 is BL 1 is UL and 2 is BR
                pt=self.winded(pt[0],pt[1],pt[2],p3)
        
                #find the coordinates of the 9 places we want to extract over
                v1=(pt[1][0]-pt[0][0], pt[1][1]-pt[0][1])
                v2=(pt[3][0]-pt[0][0], pt[3][1]-pt[0][1])
                p0=(pt[0][0],pt[0][1])
                
                ep=[]
                midpts=[]
                i=1
                j=5
                for k in range(9):
                    ep.append((p0[0]+i*v1[0]/6.0+j*v2[0]/6.0, p0[1]+i*v1[1]/6.0+j*v2[1]/6.0))
                    i=i+2
                    if i==7:
                        i=1
                        j=j-2
                        
                rad= self.ptdst(v1,(0.0,0.0))/6.0
                cs=[]
                hsvcs=[]
                den=2
                print "="*20
                for i,p in enumerate(ep):
                    if p[0] > rad and p[0]< self.W - rad and p[1] > rad and p[1] < self.H - rad:
                        
                        #valavg=val[int(p[1]-rad/3):int(p[1]+rad/3),int(p[0]-rad/3):int(p[0]+rad/3)]
                        #mask=cv.CreateImage(cv.GetDims(valavg), 8, 1 )
                        print i, "-----------------------"
                        #print "p",p
                        p = (int(round(p[0])), int(round(p[1])))
                        #print "p",p ## center of the circle
                        #print "sg",self.sg ## img
                        rad = int(rad)
                        #print "rad",rad ## radius of the circle
                        col=cv.Avg(self.sgc[int(p[1]-rad/den):int(p[1]+rad/den),int(p[0]-rad/den):int(p[0]+rad/den)])
                        print "col", col
                        cv.Circle(self.sg, p, rad, col,-1)
                        if i==4:
                            cv.Circle(self.sg, p, rad, (0,255,255),2)
                        else:
                            cv.Circle(self.sg, p, rad, (255,255,255),2)
                            
                        hueavg= cv.Avg(self.hue[int(p[1]-rad/den):int(p[1]+rad/den),int(p[0]-rad/den):int(p[0]+rad/den)])
                        satavg= cv.Avg(self.sat[int(p[1]-rad/den):int(p[1]+rad/den),int(p[0]-rad/den):int(p[0]+rad/den)])
                        
                        cv.PutText(self.sg, `int(hueavg[0])`, (p[0]+70,p[1]), ff,(255,255,255))
                        cv.PutText(self.sg, `int(satavg[0])`, (p[0]+70,p[1]+10), ff,(255,255,255))
                        
                        if extract:
                            cs.append(col)
                            hsvcs.append((hueavg[0],satavg[0]))
                            
                if extract:
                    extract= not extract
                    self.colors[selected]=cs # all faces
                    self.color = cs
                    self.looping = next_face(cs) #
                    self.hsvs[selected]=hsvcs
                    selected=min(selected+1,5)
                    
            #draw faces of hte extracted cubes
            x=20
            y=20
            s=13
            for i in range(6):
                if not self.colors[i]: 
                    x+=3*s+10
                    continue
                #draw the grid on top
                cv.Rectangle(self.sg, (x-1,y-1), (x+3*s+5,y+3*s+5), (0,0,0),-1)
                x1,y1=x,y
                x2,y2=x1+s,y1+s
                for j in range(9):
                    if self.didassignments:
                        cv.Rectangle(self.sg, (x1,y1), (x2,y2), mycols[self.assigned[i][j]],-1)
                    else:
                        cv.Rectangle(self.sg, (x1,y1), (x2,y2), self.colors[i][j],-1)
                    x1+=s+2
                    if j==2 or j==5: 
                        x1=x
                        y1+=s+2
                    x2,y2=x1+s,y1+s
                x+=3*s+10
        
            #draw the selection rectangle
            x=20
            y=20
            for i in range(selected):x+=3*s+10
            cv.Rectangle(self.sg, (x-1,y-1), (x+3*s+5,y+3*s+5), (0,0,255),2)
        
            self.lastdetected= len(li)
            #swapping for LK
            prev_grey, grey = grey, prev_grey
            prev_pyramid, pyramid = pyramid, prev_pyramid
            #draw img
        
        
            #cv.CvtColor(sg,sg2,cv.CV_RGB2HSV)
            #cv.Split(sg2, hue, sat, val, None)
        
            #cv.Smooth(sg,sg,cv.CV_GAUSSIAN, 5)
            cv.ShowImage("Fig",self.sg)
        
            counter+=1 #global counter
            # handle events
            c = cv.WaitKey(10) % 0x100
            
            if c == 27: break #ESC

            # processing depending on the character
            if 32 <= c and c < 128:
                cc = chr(c).lower()
                if cc== ' ':
                    print "pressed space"

                    

              #if cc=='r':
              #  #reset
              #  extract=False
              #  selected=0
              #  self.colors=[[] for i in range(6)]
              #  self.didassignments=False
              #  self.assigned=[[-1 for i in range(9)] for j in range(6)]
              #  for i in range(6):
              #      self.assigned[i][4]=i    
              #  self.didassignments=False
        
                if cc=='n':
                    selected=selected-1
                    if selected<0: selected=5
                if cc=='m':
                    selected=selected+1
                    if selected>5: selected=0
        
                #if cc=='b':
                #    self.onlyBlackCubes=not self.onlyBlackCubes
                #if cc=='d':
                #    self.dodetection=not self.dodetection
                if cc=='q':
                    print self.hsvs

                #if cc=='p':
                #    #process!!!!
                #    self.processColors(True)
                if cc=='u':
                    self.didassignments=not self.didassignments
                #if cc=='s':
                #    cv.SaveImage("pic"+`time()`+".jpg",self.sgc)
        
        
        cv.DestroyWindow("Fig")
        return
    
if __name__ == "__main__":
    cc = CubeCapture()
    cc.run(lambda x:True)

