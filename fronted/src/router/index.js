import React, { Suspense, lazy, useEffect } from 'react';
import { Switch, Route } from 'react-router-dom'



const Home = lazy(() => import('../pages/home'));
const Census = lazy(() => import('../pages/census'));


const RouterMap = () => {

    // 初始化CompList
    useEffect(() => {

    }, [])


    return (

        <Suspense fallback={<div style={{ marginTop: 50 }}></div>} >
            <Switch>
                {/* React.lazy(() => import('./OtherComponent')); */}
                <Route path="/census" component={Census} exact ></Route>
                <Route path="/" component={Home} exact ></Route>
               
            </Switch>

        </Suspense>
    )
}



export default RouterMap

// 配置所有路由