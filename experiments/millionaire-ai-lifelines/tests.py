import unittest
from arena import (AMOUNTS,calibrate,train_calibrator,play,signal,safe_at,update_belief,lifeline_material)
import random
class ArenaTests(unittest.TestCase):
 def setUp(self):self.model=train_calibrator(samples=500)
 def test_guarantees(self):
  self.assertEqual(safe_at(900),0);self.assertEqual(safe_at(1000),1000);self.assertEqual(safe_at(32000),32000)
 def test_15_questions(self):self.assertEqual(len(AMOUNTS),15)
 def test_six_contestants_valid_payouts(self):
  for name in ('Swagger','Flash','Chorus','Switch','Anchor','Compass'):
   p=play(42,name,self.model)
   self.assertIn(p.final,(0,)+AMOUNTS)
 def test_seed_repeat(self):
  x=play(50,'Compass',self.model,detail=True);y=play(50,'Compass',self.model,detail=True)
  self.assertEqual(x.log,y.log)
 def test_fifty_never_eliminates_truth(self):
  for seed in range(50):
   m=lifeline_material(seed,7,2,.5)
   self.assertNotIn(2,m['removed']);self.assertEqual(len(m['removed']),2)
 def test_lifeline_updates_normalize(self):
  m=lifeline_material(12,1,1,.6)
  for name in ('50:50','FRIEND','AUDIENCE'):
   b=update_belief([.4,.3,.2,.1],name,m,.6,'Compass')
   self.assertAlmostEqual(sum(b),1,places=6)
 def test_calibration_probabilities(self):
  v=calibrate(self.model,signal(random.Random(5),1,.5),.5)
  self.assertAlmostEqual(sum(v),1,places=6)
if __name__=='__main__':unittest.main()
