const import_label = document.getElementById("import").value;
const list = document.getElementById("list").value;
const import_file = document.getElementById("import_file").value;
const import_index = document.getElementById("import_index").value;
const work_flow = document.getElementById("work_flow").value;
const select_file = document.getElementById("select_file").value;
const select_index = document.getElementById("select_index").value;
const select_work_flow = document.getElementById("select_work_flow").value;
const selected_file_name = document.getElementById("selected_file_name").value;
const selected_index = document.getElementById("selected_index").value;
const selected_work_flow = document.getElementById("selected_work_flow").value;
const index_tree = document.getElementById("index_tree").value;
const designate_index = document.getElementById("designate_index").value;
const work_flow_2 = document.getElementById("work_flow_2").value;
const item_type = document.getElementById("item_type").value;
const flow = document.getElementById("flow").value;
const select = document.getElementById("select").value;
const cancel = document.getElementById("cancel").value;
const workflows = JSON.parse($("#workflows").text() ? $("#workflows").text() : "");


class MainLayout extends React.Component {

    componentDidMount() {
      console.log("import is work");
      console.log("cancel", cancel);
    }

    render() {
      return(

        <div>
          <ul className="nav nav-tabs">
            <li role="presentation" className="active"><a href="#">{import_label}</a></li>
            <li role="presentation"><a href="#">{list}</a></li>
          </ul>

          <ImportComponent></ImportComponent>
        </div>
      )
    }
}

class ImportComponent extends React.Component {

    constructor(){
      super()
      this.state = {
        file: null,
        file_name: "",
        isShowModalWF: false,
        work_flow_data : {},
        wl_key: null
      }
      this.handleChangefile = this.handleChangefile.bind(this)
      this.handleClickFile = this.handleClickFile.bind(this)
      this.getLastString = this.getLastString.bind(this)
      this.handleShowModalWorkFlow = this.handleShowModalWorkFlow.bind(this)
      this.handleChangeWF = this.handleChangeWF.bind(this)
    }

    componentDidMount() {
      console.log("ImportComponent is work");
    }

    handleChangefile (e) {
      const file = e.target.files[0],
            reader = new FileReader();
        const file_name = this.getLastString(e.target.value, "\\")
        if (this.getLastString(file_name,".") !== 'tsv') {
          return false
        }

        this.setState({
          file_name:file_name,
         });

        reader.onload = (e) => {
            this.setState({
                file: reader.result,
            });
        }
        reader.readAsDataURL(file);
    }

    handleClickFile() {
      this.inputElement.click();
    }

    getLastString(path, code){
      const split_path = path.split(code)
      return split_path.pop()
    }

    handleShowModalWorkFlow(data) {
      const {isShowModalWF} = this.state
      if(!isShowModalWF) {
        this.setState({
          isShowModalWF: !isShowModalWF
        })
      } else {
        this.setState({
          isShowModalWF: !isShowModalWF,
          work_flow_data: data ? data : null
        })
      }
    }

    handleChangeWF(e) {
      value = e.target.value
      this.setState({
        wl_key: value
      })
    }

    render() {
      const {file_name,isShowModalWF,wl_key,work_flow_data} = this.state
      return(
        <div className="container import_component">
          <div className="row layout">
            <div className="col-md-12">
              <div className="row">
                <div className="col-md-2">
                  <label>{import_file}</label>
                </div>
                <div className="col-md-8">
                  <div>
                    <button className="btn btn-primary" onClick={this.handleClickFile}>{select_file}</button>
                    <input
                      type="file"
                      className="input-file"
                      ref={input => this.inputElement = input}
                      accept=".tsv"
                      onChange={this.handleChangefile}
                      />
                  </div>
                  <div className="block-placeholder">
                    {
                      file_name ? <p className="active">{file_name}</p> : <p>{selected_file_name}</p>
                    }
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-12">
              <div className="row">
                <div className="col-md-2">
                  <label>{import_index}</label>
                </div>
                <div className="col-md-8">
                  <div>
                    <button className="btn btn-primary">{select_index}</button>
                  </div>
                  <div className="block-placeholder">
                    <p>{selected_index}</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-12">
              <div className="row">
                <div className="col-md-2">
                  <label>{work_flow}</label>
                </div>
                <div className="col-md-8">
                  <div>
                    <button className="btn btn-primary" onClick={this.handleShowModalWorkFlow}>{select_work_flow}</button>
                  </div>
                  <div className="block-placeholder">
                    {
                      work_flow_data ? <p className="active">{work_flow_data.flows_name}</p> : <p>{selected_work_flow}</p>
                    }
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-12">
              <div className="row">
                <div className="col-md-2">
                  <button className="btn btn-primary">
                    <span className="glyphicon glyphicon-download-alt icon"></span>{import_label}
                    </button>
                    </div>
              </div>
            </div>
          </div>
          <div className={`modal ${isShowModalWF ? "active" : ''}`}>
            <div className="modal-mark" onClick={this.handleShowModalWorkFlow}></div>
            <div className="modal-content">
            <div class="row">
              <div class="col-sm-12 header">
                <h3>{work_flow}</h3>
              </div>
              <div class="col-sm-12">
                <table class="table table-striped table-bordered">
                  <thead>
                    <tr>
                      <th></th>
                      <th>{work_flow}</th>
                      <th>{item_type}</th>
                      <th>{flow}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {
                      workflows.map((item, key) => {
                        return (
                          <tr>
                            <td style={{textAlign: 'center'}}>
                              <input 
                                type='radio'
                                name='workflow' 
                                value={key} 
                                onChange={this.handleChangeWF}
                                ></input>
                            </td>
                            <td>{item.flows_name}</td>
                            <td>{item.item_type_name}</td>
                            <td>{item.flow_name}</td>
                          </tr>
                        )
                      })
                    }
                  </tbody>
                </table>
              </div>
              <div class="col-sm-12 footer text-align-right">
                <button className="btn btn-primary" onClick={()=>{this.handleShowModalWorkFlow(workflows[wl_key])}}><span className="glyphicon glyphicon-download-alt icon"></span>{select}</button>
                <button className="btn btn-danger m-l-15" onClick={this.handleShowModalWorkFlow}>{cancel}</button>
              </div>
            </div>             
            </div>
          </div>
        </div>
      )
    }
}

$(function () {
    ReactDOM.render(
        <MainLayout/>,
        document.getElementById('root')
    )
});
