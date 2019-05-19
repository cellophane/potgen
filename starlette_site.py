from starlette.applications import Starlette
import uvicorn
from starlette.responses import FileResponse
from potgen import PotGen
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
import ast
from scipy.interpolate import UnivariateSpline
from starlette.routing import Router, Mount
app = Router(routes=[
    Mount('/static', app=StaticFiles(directory='static'), name="static"),
])
@app.route("/")
def form(request):
    return HTMLResponse("""
        <h3>Generate your own 3D-printable pot!<h3>
        <form action="generate" enctype="multipart/form-data">
            parameters for the profile: x values must be increasing.
            x values:
            <input type="text" name="x" value="[0,5,7,8,12]">
            y values:
            <input type="text" name="y" value = "[2,3,1.75,1.5,3]">
            resolution [zRes,thetaRes]:
            <input type="text" name="res" value = "[16,4]">
            <input type="submit" value="create pot!">
        </form>
        
    """)

@app.route("/test")
def test(request):
    return HTMLResponse("""<literal>
<iframe width="600" height="800" frameborder="0" scrolling="no" src="static/test1.html"></iframe>
</literal>""")
@app.route("/testgen/{zRes}/{thetaRes}")
def testGen(request):
    zRes = int(request.path_params['zRes'])
    thetaRes = int(request.path_params['thetaRes'])
    x = [0,5,10,15]
    y = [2,4,1.5,2]
    curve = UnivariateSpline(x, y)
    res = [zRes,thetaRes]
    pot = PotGen(curve,res)
    pot.generate()
    pot.save()
    return FileResponse('pot.stl',filename = 'pot.stl')
@app.route("/generate")
def generate(request):
    xString = request.query_params['x']
    yString = request.query_params['y']
    resString = request.query_params['res']
    x = ast.literal_eval(xString)
    y = ast.literal_eval(yString)
    res = ast.literal_eval(resString)
    curve = UnivariateSpline(x, y)
    pot = PotGen(curve,res)
    pot.generate()
    pot.save()
    
    return FileResponse('pot.stl',filename = 'pot.stl')

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5225)