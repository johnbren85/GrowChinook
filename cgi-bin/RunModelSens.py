#!/usr/bin/python

import os
import matplotlib
matplotlib.use('Agg')
import sys
import csv
from Bioenergetics import *
import cgi, cgitb
import pylab
import io
from PIL import Image, ImageDraw
import base64
from scipy.interpolate import griddata
import pandas
import seaborn
cgitb.enable()

form = cgi.FieldStorage()
# Get data from fields

StartingMass = form.getvalue('Starting_Mass_In')
TempCurve = form.getvalue('tempCurve')
if StartingMass != None:
    StartingMass=float(StartingMass)
else:
    StartingMass = 40

if form.getvalue('defa') == 'yes':
    def_flag = 'YES'
else:
    def_flag = 'NO'

if form.getvalue('depr') == 'yes':
    depr_flag = 'YES'
else:
    depr_flag = 'NO'

if def_flag == 'YES':
    Total_Daphnia = None
    DaphSize = None
    TempCurve = None
    Month = form.getvalue('Month')
    Month2 = form.getvalue('Month')
    Light = None
    Year = form.getvalue('Year')
    Site = form.getvalue('Site')

else:
    Total_Daphnia = form.getvalue('Total_Daphnia_Input_Name')
    if Total_Daphnia != None:
        Total_Daphnia = float(Total_Daphnia)
    DaphSize  = form.getvalue('Daphnia Size')
    if DaphSize != None:
        DaphSize = float(DaphSize)
    Light = form.getvalue('Light')
    if Light != None:
        Light = float(Light)
    Month = form.getvalue('Month')
    Month2 = form.getvalue('Month')
    Year = form.getvalue('Year')
    Site = form.getvalue('Site')

if depr_flag == 'YES':
    Dmax = float(form.getvalue('DmaxIn'))
    Dmin = float(form.getvalue('DminIn'))
else:
    Dmax = 10000
    Dmin = -1

print ('Content-type:text/html; charset=utf-8\r\n\r\n')
print ('<html>')
print('''<link type="text/css" rel="stylesheet" media="screen" href="/css/Style.css" />
<img class="head" src="/css/src/LPR.jpg">
<head>
    <title>GrowChinook</title>
</head>
<body>
    <ul>
        <li><a href="http://cas-web0.biossys.oregonstate.edu/">Home</a></li>
        <li><a href="http://cas-web0.biossys.oregonstate.edu/Test.py">Run Standard Model</a></li>
        <li><a class="current" href="http://cas-web0.biossys.oregonstate.edu/TestSens.py">Run Model With Sensitivity</a></li>
        <li><a href="http://cas-web0.biossys.oregonstate.edu/TestSens2.py">Run Advanced Sensitivity</a></li>
        <li><a href="http://cas-web0.biossys.oregonstate.edu/about.html">About</a></li>
    </ul>''')
print ('<head>')
print ('<title>Here are Your Results.</title>')
print ('</head>')

Light,Total_Daphnia,DaphSize = GetVals(Light,Total_Daphnia,DaphSize,Site,Month,Year)
FreshBatch = Batch(Site, Month, Year, Light, DaphSize, Total_Daphnia, StartingMass, Dmax, Dmin,TempCurve)
BaseResults,DConsumed  = FreshBatch.Run_Batch()

largestout = 0.0
batches = []
results = []
SensInputs = []
SensFactors = []
SensOutPer = []
SensOutPerD1 = []
if form.getvalue('Sparam_Range') != None:
    Sparam_Range = float(form.getvalue('Sparam_Range'))
else:
   Sparam_Range = 0.75
SensParam = form.getvalue('Sens_Param')
SensFactors = Sensitivity_Expand(Sparam_Range, SensFactors)

if SensParam == 'Starting Mass':
    Sparam = StartingMass
    for i in range(11):
        if (Sparam * SensFactors[i] + Sparam) > 0:
            SensInputs.append(Sparam * SensFactors[i] + Sparam)
            SensFactors[i] = SensFactors[i] * 100
            batches.append(Batch(Site, Month, Year, Light, DaphSize, Total_Daphnia, SensInputs[i],Dmax,Dmin,TempCurve))
            results.append(batches[i].Run_Batch())
            SensOutPer.append(results[i][0]['growth'][29])
            SensOutPerD1.append(results[i][0]['growth'][0])
        else:
            SensInputs.append(None)       
            batches.append(None)
            results.append(None)
            SensOutPer.append(None)
            SensOutPerD1.append(None)

elif SensParam == 'Total Daphnia':
    Sparam = Total_Daphnia
    for i in range(11):
        SensInputs.append(Sparam * SensFactors[i] + Sparam)
        SensFactors[i] = SensFactors[i] * 100
        batches.append(Batch(Site, Month, Year, Light, DaphSize, SensInputs[i], StartingMass,Dmax,Dmin,TempCurve))
        results.append(batches[i].Run_Batch())
        SensOutPer.append(100 * ((results[i][0]['growth'][29] - BaseResults['growth'][29]) / BaseResults['growth'][29]))
        SensOutPerD1.append(100 * ((results[i][0]['growth'][0] - BaseResults['growth'][0]) / BaseResults['growth'][0]))

elif SensParam == 'Daphnia Size':
    Sparam = DaphSize
    for i in range(11):
        SensInputs.append(Sparam * SensFactors[i] + Sparam)
        SensFactors[i] = SensFactors[i] * 100
        batches.append(Batch(Site, Month, Year, Light, SensInputs[i], Total_Daphnia, StartingMass,Dmax,Dmin,TempCurve))
        results.append(batches[i].Run_Batch())
        SensOutPer.append(100 * ((results[i][0]['growth'][29] - BaseResults['growth'][29]) / BaseResults['growth'][29]))
        SensOutPerD1.append(100 * ((results[i][0]['growth'][0] - BaseResults['growth'][0]) / BaseResults['growth'][0]))

elif SensParam == 'K':
    Sparam = k
    for i in range(11):
        SensInputs.append(Sparam * SensFactors[i] + Sparam)
        SensFactors[i] = SensFactors[i] * 100
        batches.append(Batch(Site, Month, Year, SensInputs[i], DaphSize, Total_Daphnia, StartingMass,Dmax,Dmin,TempCurve))
        results.append(batches[i].Run_Batch())
        SensOutPer.append(100 * ((results[i][0]['growth'][29] - BaseResults['growth'][29]) / BaseResults['growth'][29]))
        SensOutPerD1.append(100 * ((results[i][0]['growth'][0] - BaseResults['growth'][0]) / BaseResults['growth'][0]))
     # "Daphnia eaten",results[0]['dailyconsume'][x])
for i in range(len(SensFactors)):
    if SensFactors[i] != None:
        if abs(SensFactors[i]) > abs(largestout):
            largestout = abs(SensFactors[i])
for i in range(len(SensOutPer)):
    if SensOutPer[i] != None:
        if abs(SensOutPer[i]) > abs(largestout):
            largestout = abs(SensOutPer[i])
if abs(largestout) > 30000:
    largestout = 30000
largestoutrem = largestout % 50
largestout = largestout + 50 - largestoutrem
fig=pyplot.figure()
fig=pyplot.figure(facecolor='#c8e9b1')
ax = fig.add_subplot(122)
ax.plot(SensFactors, SensOutPer, 'g^')
if SensParam == 'Starting Mass':
    ax.set_ylabel('Final Growth Rate')
else:
    ax.set_ylabel('Percent Change in Final Growth Rate')
    ax.axis([-largestout, largestout, -largestout, largestout])
    ax.set_aspect('equal', adjustable='box')
ax.set_xlabel('Percent Change in %s' % SensParam)
ax.grid()
ax1 = fig.add_subplot(121)
ax1.plot(SensFactors, SensOutPerD1, 'o')
if SensParam == 'Starting Mass':
    ax1.set_ylabel('Final Growth Rate')
else:
    ax1.set_ylabel('Percent Change in Final Growth Rate')
    ax1.axis([-largestout, largestout, -largestout, largestout])
    ax1.set_aspect('equal', adjustable='box')
ax1.set_xlabel('Percent Change in %s' % SensParam)
ax1.grid()
fig.tight_layout(pad=1.08, h_pad=None, w_pad=None, rect=None)
pylab.savefig( "new.png",facecolor=fig.get_facecolor(), edgecolor='lightblue')
data_uri = base64.b64encode(open('new.png', 'rb').read()).decode('utf-8').replace('\n', '')
img_tag = '<img class="results" src="data:image/png;base64,{0}">'.format(data_uri)
print(img_tag)

print ('''
    <br>
    <div id="valuewraps">
        <div id="datahead">
            %s, %s
        </div>
        <div id="indata">
            <div class="dataleft">Input Values:</div>
            <div class="dataleft">%s Starting Mass:
                <div class="dataright">%.1f g</div>
            </div>
            <div class="dataleft">%s Total Daphnia:
                <div class="dataright">%.0f</div>
            </div>
            <div class="dataleft">%s Daphnia Size:
                <div class="dataright">%.2f mm</div>
            </div>
            <div class="dataleft">%s Light Extinction Coefficient:
                <div class="dataright">%.2f</div>
            </div>
       ''' % (FreshBatch.Site,FreshBatch.Year,Month,StartingMass,Month,FreshBatch.TotalDaphnia,Month,FreshBatch.DaphSize,Month,FreshBatch.Light))

if depr_flag == "YES":
    print('''Depth restricted to between %.2fm and %.2fm.<br>''' % (Dmin,Dmax))

print ('''  </div>
            <div id="outdata">
                <div class="dataleft">Output Values:</div>
                <div class="dataleft">%s Final Mass at +%.0f percent:
                    <div class="dataright">%.1f g</div>
                </div>
                <div class="dataleft">%s Final Mass at -%.0f percent:
                    <div class="dataright">%.1f g</div>
                </div>
                <div class="dataleft">%s Final Daily Growth:
                    <div class="dataright">%.1f g/g/day</div>
                </div>
                <div class="dataleft">%s Final Day Depth:
                    <div class="dataright">%.0f m</div>
                </div>
                <div class="dataleft">%s Final Night Depth:
                    <div class="dataright">%.0f m</div>
                </div>
                <div class="dataleft">%s Total Daphnia Consumed:
                    <div class="dataright">%.0f</div>
                </div>
            </div>
       </div>
       </div><br>
       ''' % (Month,SensFactors[10],results[10][0]['StartingMass'][29],Month,SensFactors[10],results[0][0]['StartingMass'][29],Month,BaseResults['growth'][29],Month,BaseResults['day_depth'][29],Month,BaseResults['night_depth'][29],Month,DConsumed))

print('''
<script type="text/javascript">
    function configureDropDownLists(ddy,ddm,dds) {
    var years = ['2013', '2014', '2015'];
    var months = ['March', 'April', 'May', 'June', 'July', 'August'];
    var sites = ['Blue River', 'Fall Creek', 'Hills Creek', 'Lookout Point'];

    switch (ddy.value) {
        case '2013':
            ddm.options.length = 0;
            createOption(ddm, months[3], months[3]);
            createOption(ddm, months[5], months[5]);
            dds.options.length = 0;
            for (i=0; i<3; i++) {
                createOption(dds,sites[i],sites[i]);
            }
            break;
        case '2014':
            ddm.options.length = 0;
        for (i = 3; i < months.length; i++) {
            createOption(ddm, months[i], months[i]);
            }
        dds.options.length = 0;
        for (i=1; i<sites.length; i++) {
                createOption(dds,sites[i],sites[i]);
            }
            break;
        case '2015':
            ddm.options.length = 0;
            for (i = 0; i < months.length; i++) {
                createOption(ddm, months[i], months[i]);
            }
            dds.options.length = 0;
            for (i=1; i<sites.length; i++) {
                createOption(dds,sites[i],sites[i]);
            }
            break;
        default:
            ddm.options.length = 0;
        break;
    }

}

    function createOption(dd, text, value) {
        var opt = document.createElement('option');
        opt.value = value;
        opt.text = text;
        dd.options.add(opt);
    }
</script>
<script>
function updateDepthTextInput(val) {
          document.getElementById('DMaxInID').value=val;
          document.getElementById('DmaxOutID').value=val;
          document.getElementById('DMinInID').value=val;
          document.getElementById('DminOutID').value=val;
        }
</script>
<script>
function updateSMassInput(val) {
          document.getElementById('SMass_TextInID').value=val;
        }
</script>
<script>
function updateDaphSText(val) {
          document.getElementById('DaphSTextInID').value=val;
        }
</script>
<script>
function updateTotDTextInput(val) {
          document.getElementById('TotDTextInID').value=val;
        }
</script>
<script>
function updateLightTextInput(val) {
          document.getElementById('LightTextInID').value=val;
        }
</script>
<body>
    <h2>Enter Values to GrowChinook</h2>
    <div id="formwrap">
        <form action="RunModelSens.py" method="post" target="_blank">
            <div id="sec1">
                <label>Please Select Year:</label> <select name="Year" id="ddy" onchange="configureDropDownLists(this,document.getElementById('ddm'),document.getElementById('dds'))">
                    <option value=""></option>
                    <option value="2013">2013</option>
                    <option value="2014">2014</option>
                    <option value="2015">2015</option>
                </select>
                <br>
                <br>

                <label>Please Select Site:</label> <select name="Site" id="dds">
                </select>
                <br>
                <br>

                <label>Please Select Month:</label> <select name="Month" id="ddm">
                </select>
                <br>
                <br>
                    <div style="text-align:center;font-size:20px;">Use Default Values? </div><br>
                <label>Yes</label><input type="radio" name="defa" value="yes" /><br>
                <label>No</label><input type="radio" name="defa" value='no' /><br><br>

                <label>Fish Starting Mass (g):</label><input type="range" name="SMassSlide" id="SMassInID" value="60" min="0" max="200" step="0.1" onchange="updateSMassInput(this.value);" oninput="SMassOut.value = SMassSlide.value"><output name="SMassOut" id="SMassOutID">.75</output>
                <label>Or Enter Value:</label> <input type="text" name="Starting_Mass_In" id="SMass_TextInID"  oninput="SMassOutID.value = SMass_TextInID.value"> <br><br>

                <label>Daphnia Size (mm):</label><input type="range" name="DaphSSlide" id="DaphSInID" value=".75" min=".5" max="1.5" step=".01" onchange="updateDaphSText(this.value);" oninput="DaphSOut.value = DaphSSlide.value"><output name="DaphSOut" id="DaphSOutID">.75</output><br><br>
                <label>Or Enter Value:</label> <input type="text" name="Daphnia Size" id="DaphSTextInID" oninput="DaphSOutID.value = DaphSTextInID.value"> <br>
            </div>
            <div id="sec2">
                <label>Total Daphnia:</label><input type="range" name="TotDSlide" id="TotDInID" value="500" min="0" max="1000" onchange="updateTotDTextInput(this.value);" oninput="TotDOut.value = TotDSlide.value"><output name="TotDOut" id="TotDOutID"> 500 </output><br><br>
                <label>Or Enter Value:</label> <input type="text" name="Total_Daphnia_Input_Name" id="TotDTextInID" oninput="TotDOutID.value = TotDTextInID.value" oninput="TotDOutID.value = TotDInID.value"> <br>

                <label>Light Extinction Coefficient:</label><input type="range" name="LightSlide" id="LightInID" value=".3" min="0" max="1" step=".01" onchange="updateLightTextInput(this.value);" oninput="LightOut.value = LightSlide.value"><output name="LightOut" id="LightOutID">.3</output><br><br>
                <label>Or Enter Value:</label> <input type="text" name="Light" id="LightTextInID" oninput="LightOutID.value = LightTextInID.value" oninput="LightOutID.value = LightInID.value"> <br><br>

                    <div style="text-align:center;font-size:20px;">Restrict Depth?</div><br>
                <label>Yes</label><input type="radio" name="depr" value="yes" /><br>
                <label>No</label><input type="radio" name="depr" value="no" /><br>
                <label>Maximum Depth:</label><input type="range" name="DmaxIn" id="DmaxInID" value="60" min="0" max="200" oninput="DmaxOutID.value = DmaxInID.value" onchange="updateDepthTextInput(this.value);"><output name="DmaxOut" id="DmaxOutID"> 60 </output> <br>
                <label>Minimum Depth:</label><input type="range" name="DminIn" id="DminInID" value="60" min="0" max="200" oninput="DminOutID.value = DminInID.value" onchange="updateDepthTextInput(this.value);"><output name="DminOut" id="DminOutID"> 60 </output> <br>
                <label>Or Restrict to a Single Depth:</label> <input type="text" name="Depth_Text" id="Depth_TextInID" oninput="DminIn.value = Depth_Text.value; DmaxIn.value = Depth_Text.value"> <output name="Depth_TextOut" id="Depth_TextOutID"> </output> <br><br>
            </div><br>
            
                <div style="display:inline-block;width:1100px;">
                    <div style="width:300px;"></div>
                    <div style="font-size:20px;width:500px;margin:auto;">Select Sensitivity Parameter:<select name="Sens_Param"><br>
                        <option value="Starting Mass" selected>Starting Mass</option>
                        <option value="Total Daphnia">Total Daphnia</option>
                        <option value="Daphnia Size">Daphnia </option>
                        <option value="K">Light</option>
                    </select>
                    </div>
                    <div style="width:300px;"></div>
                    <br>
                    <label>Select Sensitivity Range(percent)</label><input type="range" name="SensSlide" id="SensInID" value=".50" min=".01" max="1.50" step=".01" onchange="updateSensText(this.value);" oninput="SensOut.value = SensSlide.value"><output name="SensOut" id="SensOutID">.50</output><br><br>
                    <label>Or Enter Value:</label> <input type="text" name="Sparam_Range" id="SensTextInID" oninput="SensOutID.value = SensTextInID.value"> <br>
                    <div id="subutt">
                        <input type="submit" value="Submit"/>
                    </div>
        </form>
    </div>
</body>
''')

os.remove('new.png')
quit()