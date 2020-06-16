import numpy as np
left_target = np.array([113.5, 99, 112])
print('target:')
print(left_target)

ring = 90
arc=90

r =(-ring)*(np.pi/180)
ringTrans = np.array([1,0,0, 0,np.cos(r),-np.sin(r), 0,np.sin(r),np.cos(r)]).reshape([3,3])
a=(-arc)*(np.pi/180)

#arcTrans = np.array([ np.cos(arc),0,np.sin(arc), 0,1,0, -np.sin(arc),0,np.cos(arc)]).reshape([3,3])
arcTrans = np.array([ np.cos(a), -np.sin(a),0, np.sin(a),np.cos(a),0, 0,0,1]).reshape([3,3])

trajTrans = np.dot(ringTrans, arcTrans)

# in the source refence space:
# x is positive from th target onwards (minus is before the target)
# y is positive to the left
# z is positive front
# --> for the bengun:
# center: [0,0,0]
# anterior: [0,0,2]
# posterior: [0,0,-2]
# left lateral, right medial: [0,2,0]
# left medial, right lateral: [0,-2,0]

print(left_target + np.dot(trajTrans, np.array([-0,0,2])))
