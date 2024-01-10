import { ComponentProps, render } from 'preact';
import { signal } from "@preact/signals";

import axios, {isCancel, AxiosError} from 'axios';

import './style.css';
import { PropsWithChildren, useEffect, useState } from 'preact/compat';
import { PatternList } from './components/PatternList';
import { Filter } from './components/Filter';
import { Title } from './components/Title';
import { Footer } from './components/Footer';

//TODO move me
interface Filters {

}

export function App() {
	const [data, setData] = useState([]);
	const [schema, setSchema] = useState([]);

	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	useEffect(() => {
			const fetchData = async () => {
					try {
							const response = await axios.get('/patterns');
							setData(response.data);
					} catch (error) {
							setError(error);
					} finally {
							// setLoading(false);
					}
			};

			const fetchSchema = async () => {
				try {
						const response = await axios.get('/schema');
						setSchema(response.data);
				} catch (error) {
						setError(error);
				} finally {
						setLoading(false);
				}
		};

			fetchData();
			fetchSchema();
	}, []); // The empty dependency array ensures that this effect runs only once, equivalent to componentDidMount in class components

	if (loading) {
			return <div>Loading...</div>;
	}

	if (error) {
			return <div>Error: {error.message}</div>;
	}

	// Filter state and mutators
	const [ filters, setFilter ] = useState([]);

	function addFilter(key, value) {
		const new_filters = [
			...filters, {[key]: value}
		]
		setFilter(new_filters);
	}

	function removeFilter(key, value) {
		const new_filters = filters.filter(f => !(key in f && f[key] == value));
		setFilter(new_filters);
	}

	function toggleFilter(key, value) {
		if (!filters.some(f => key in f && f[key] == value)) {
			addFilter(key, value);
		} else {
			removeFilter(key, value);
		}
	}

	return (
		<div>
			<Title />
			<Filter 
				filterSchema={schema[0]} 
				filters={filters}
				toggleFilter={toggleFilter}
			/>
			<PatternList 
				data={data}
				filters={filters} 
			/>
			<Footer />
		</div>
	);
}

render(<App />, document.getElementById('app'));
