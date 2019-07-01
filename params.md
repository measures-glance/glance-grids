---
layout: default
---

# Parameters

## CRS Table
<table style="table-layout: fixed; width: 100%; font-family: 'Roboto Mono', monospace;">
<th>Continent Name</th>
<th>CRS</th>
{% for continent in site.data.GLANCE_param %}
    {% assign cont_name = continent[0] %}
    {% assign cont_data = continent[1] %}
    <tr>
        <td>{{ cont_name }}</td>
        <td style="word-break:break-all;">{{ cont_data.crs }}</td>
    </tr>
    
    
{% endfor %}
</table>


## Continents
{% for continent in site.data.GLANCE_param %}
{% assign cont_name = continent[0] %}
{% assign cont_data = continent[1] %}
### {{ cont_name }}
<table style="table-layout: fixed; width: 100%; font-family: 'Roboto Mono', monospace;">
    <tr>
	    <th>Grid Name</th>
	    <td>{{ cont_data.name }}</td>
	</tr>
	<tr>
        <th>Upper Left</th>
        <td>
            <ul>
                <li> X: {{ cont_data.ul[0] }}</li>
                <li> Y: {{ cont_data.ul[1] }}</li>
            </ul>    	
        </td>
    </tr>
    <tr>
        <th>CRS</th>
        <td style="word-break:break-all;">{{cont_data.crs}}</td>
    </tr>
    <tr>
        <th>Pixel Size</th>
        <td>
            <ul>
                <li> X: {{ cont_data.res[0] }}</li>
                <li> Y: {{ cont_data.res[1] }}</li>
            </ul>    	
    	</td>
    </tr>
    <tr>
        <th>Tile Size</th>
        <td>
            <ul>
                <li> X: {{ cont_data.size[0] }}</li>
                <li> Y: {{ cont_data.size[1] }}</li>
            </ul>    	
    	</td>
    </tr>
    <tr>
    <th>Tile Grid Limits</th>
    <td>
            <ul>
                <li> Row Range: ({{ cont_data.limits[0][0] }} , {{ cont_data.limits[0][1] }})</li>
                <li> Col Range: ({{ cont_data.limits[1][0] }} , {{ cont_data.limits[1][1] }})</li>
            </ul>    	
    	</td>
    </tr>

</table>
{% endfor %}
