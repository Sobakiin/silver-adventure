import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://serviceapp-will.westus3.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Immediate orders</th>
							<th>Scheduled orders</th>
						</tr>
						<tr>
							<td># Number of orders: {stats['num_orders']}</td>
							<td># Number of scheduled: {stats['num_schedules']}</td>
						</tr>
						<tr>
							<td colspan="2">Most Requested Destination: {stats['most_requested_destination']}</td>
						</tr>
						<tr>
							<td colspan="2">Average passengers: {stats['mean_passengers']}</td>
						</tr>
						<tr>
							<td colspan="2">Most frequently requested time of arrival: {stats['most_frequent_arrival']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}

