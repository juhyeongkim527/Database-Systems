#include <iostream>
#include <vector>
#include <cstring>
#include <fstream>
#include <sstream>
#include <cmath>
using namespace std;

char *index_file_name;
char *data_file_name;

class Node
{
public:
    int num_of_keys;            // 현재 노드에 있는 Key의 개수
    vector<int> keys;           // 노드에 있는 Key를 저장하는 벡터
    vector<long> left_children; // internal node : key에 해당하는 left child Node에 대한 파일 오프셋을 저장하는 벡터
    vector<int> values;         // leaf node     : Key에 대응되는 value를 저장하는 벡터
    long right_node;            // internal node : rightmost child node / leaf node : right sibling node
    long file_offset;           // 파일 내에서 해당 노드의 위치(offset)
    long parent_node;           // 부모 노드의 파일 오프셋
    bool is_leaf;               // leaf node인지 여부

    Node(int max_num_of_child_nodes, long file_offset, bool is_leaf)
    {
        this->num_of_keys = 0;
        keys.resize(max_num_of_child_nodes);
        left_children.resize(max_num_of_child_nodes + 1);
        values.resize(max_num_of_child_nodes);
        this->right_node = 0;
        this->file_offset = file_offset;
        this->parent_node = 0;
        this->is_leaf = is_leaf;
    }

    int find_key_index(int key) // 한 노드 내에서 key가 들어갈 수 있는 idx를 리턴
    {
        int idx = 0;
        while (idx < num_of_keys && key >= keys[idx])
            idx++;

        return idx;
    }

    void print_all_keys() // 한 노드 내에 있는 모든 key를 출력
    {
        for (int idx = 0; idx < num_of_keys - 1; idx++)
            cout << keys[idx] << ", ";
        cout << keys[num_of_keys - 1] << '\n';
    }
};

class BPTree
{
public:
    fstream index_file;
    int max_num_of_child_nodes;
    int min_num_of_keys;
    long root_offset;
    Node *root;

    BPTree() // BPTree의 metadata(최대 자식 노드의 개수, root node의 offset)를 읽어와서 저장
    {
        index_file.open(index_file_name, ios::in | ios::out | ios::binary);

        if (!index_file)
        {
            cout << "<Error>" << '\n'
                 << "index file open failed" << '\n';
            exit(1);
        }

        index_file.seekg(0, ios::beg);
        index_file.read(reinterpret_cast<char *>(&max_num_of_child_nodes), sizeof(int));
        index_file.read(reinterpret_cast<char *>(&root_offset), sizeof(long));

        min_num_of_keys = int(ceil(double(max_num_of_child_nodes) / 2)) - 1;

        if (root_offset == 0)
            root = nullptr;
        else
            root = read_node_from_index_file(root_offset);
    }

    Node *read_node_from_index_file(long file_offset)
    {
        index_file.seekg(file_offset, ios::beg);
        Node *node = new Node(max_num_of_child_nodes, file_offset, false);

        index_file.read(reinterpret_cast<char *>(&node->num_of_keys), sizeof(int));
        index_file.read(reinterpret_cast<char *>(node->keys.data()), sizeof(int) * (max_num_of_child_nodes));
        index_file.read(reinterpret_cast<char *>(node->left_children.data()), sizeof(long) * (max_num_of_child_nodes + 1));
        index_file.read(reinterpret_cast<char *>(node->values.data()), sizeof(int) * (max_num_of_child_nodes));
        index_file.read(reinterpret_cast<char *>(&node->right_node), sizeof(long));
        index_file.read(reinterpret_cast<char *>(&node->file_offset), sizeof(long));
        index_file.read(reinterpret_cast<char *>(&node->parent_node), sizeof(long));
        index_file.read(reinterpret_cast<char *>(&node->is_leaf), sizeof(bool));

        return node;
    }

    void write_node_to_index_file(Node *node)
    {
        index_file.seekp(node->file_offset, ios::beg);

        index_file.write(reinterpret_cast<char *>(&node->num_of_keys), sizeof(int));
        index_file.write(reinterpret_cast<char *>(node->keys.data()), sizeof(int) * (max_num_of_child_nodes));
        index_file.write(reinterpret_cast<char *>(node->left_children.data()), sizeof(long) * (max_num_of_child_nodes + 1));
        index_file.write(reinterpret_cast<char *>(node->values.data()), sizeof(int) * (max_num_of_child_nodes));
        index_file.write(reinterpret_cast<char *>(&node->right_node), sizeof(long));
        index_file.write(reinterpret_cast<char *>(&node->file_offset), sizeof(long));
        index_file.write(reinterpret_cast<char *>(&node->parent_node), sizeof(long));
        index_file.write(reinterpret_cast<char *>(&node->is_leaf), sizeof(bool));

        index_file.flush();
    }

    void insert(int key, int value)
    {
        if (root_offset == 0) // root node가 없는 경우 : 입력 받은 key, value를 가지는 root node 생성
        {
            root = new Node(max_num_of_child_nodes, sizeof(int) + sizeof(long), true);
            root->parent_node = 0;
            root->keys[0] = key;
            root->values[0] = value;
            root->num_of_keys++;
            root_offset = root->file_offset;

            index_file.seekp(sizeof(int), ios::beg);
            index_file.write(reinterpret_cast<char *>(&root->file_offset), sizeof(long));

            write_node_to_index_file(root);
        }

        else // root node가 있는 경우 : 입력 받은 key, value를 leaf node에 삽입
        {
            Node *leaf_node = single_key_search(key, false); // 입력 받은 key에 해당하는 leaf node 찾기
            int idx = leaf_node->find_key_index(key);        // 입력 받은 key의 인덱스 찾기

            leaf_node->keys.insert(leaf_node->keys.begin() + idx, key);       // 입력 받은 key를 벡터에 삽입
            leaf_node->values.insert(leaf_node->values.begin() + idx, value); // 입력 받은 value를 벡터에 삽입
            leaf_node->num_of_keys++;

            if (leaf_node->num_of_keys <= max_num_of_child_nodes - 1) // leaf node에 공간이 있는 경우
                write_node_to_index_file(leaf_node);

            else // 노드에 공간이 없는 경우
            {
                Node *new_leaf_node = split_leaf_node(leaf_node);

                // leaf node가 split될 때는, 항상 parent node에 leaf노드에 insert한 key를 삽입해야함 (new_leaf_node->keys[0])
                insert_to_parent_node(leaf_node, new_leaf_node, new_leaf_node->keys[0]);
            }
        }
    }

    Node *split_leaf_node(Node *node)
    {
        // 노드가 겹치지 않도록 파일 끝에 새로운 노드를 생성
        index_file.seekp(0, ios::end);
        long new_file_offset = index_file.tellp();

        Node *new_right_leaf_node = new Node(max_num_of_child_nodes, new_file_offset, true);

        new_right_leaf_node->right_node = node->right_node;  // 새로운 노드의 오른쪽 포인터를 현재 노드의 오른쪽 포인터로 설정
        node->right_node = new_right_leaf_node->file_offset; // 현재 노드의 오른쪽 포인터를 새로운 노드의 파일 오프셋으로 설정

        new_right_leaf_node->parent_node = node->parent_node;

        int mid_idx = max_num_of_child_nodes / 2;
        node->num_of_keys = mid_idx;
        new_right_leaf_node->num_of_keys = max_num_of_child_nodes - mid_idx;

        for (int idx = 0; idx < new_right_leaf_node->num_of_keys; idx++)
        {
            new_right_leaf_node->keys[idx] = node->keys[idx + mid_idx];
            new_right_leaf_node->values[idx] = node->values[idx + mid_idx];
        }

        write_node_to_index_file(node);
        write_node_to_index_file(new_right_leaf_node);

        return new_right_leaf_node;
    }

    void insert_to_parent_node(Node *left_child_node, Node *new_right_child_node, int insert_key)
    {
        if (left_child_node->parent_node == 0) // child node가 root인 경우
        {

            index_file.seekp(0, ios::end);
            long new_file_offset = index_file.tellp();

            root = new Node(max_num_of_child_nodes, new_file_offset, false); // 새로운 root node 생성
            root->parent_node = 0;
            root->keys[0] = insert_key;
            root->left_children[0] = left_child_node->file_offset;
            root->right_node = new_right_child_node->file_offset;
            root->num_of_keys++;
            root_offset = root->file_offset;

            left_child_node->parent_node = root->file_offset;
            new_right_child_node->parent_node = root->file_offset;

            // index file에 root_offset 업데이트
            index_file.seekp(sizeof(int), ios::beg);
            index_file.write(reinterpret_cast<char *>(&root->file_offset), sizeof(long));

            write_node_to_index_file(root);
            write_node_to_index_file(left_child_node);
            write_node_to_index_file(new_right_child_node);
        }

        else // child node가 root가 아닌 경우
        {
            Node *parent_node = read_node_from_index_file(left_child_node->parent_node);

            new_right_child_node->parent_node = parent_node->file_offset; // 중요 : split_internal_node를 한번 더 호출하지 않을 수 있기 때문에 해줘아함

            int insert_idx = parent_node->find_key_index(insert_key);                     // 부모 노드에 삽입할 키의 인덱스를 찾음
            parent_node->keys.insert(parent_node->keys.begin() + insert_idx, insert_key); // 부모 노드에 Key 삽입
            parent_node->num_of_keys++;

            if (parent_node->right_node == left_child_node->file_offset)
            {
                parent_node->left_children.insert(parent_node->left_children.begin() + insert_idx, left_child_node->file_offset);
                parent_node->right_node = new_right_child_node->file_offset;
            }

            else
                parent_node->left_children.insert(parent_node->left_children.begin() + insert_idx + 1, new_right_child_node->file_offset);

            write_node_to_index_file(parent_node);
            write_node_to_index_file(left_child_node);
            write_node_to_index_file(new_right_child_node);

            if (parent_node->num_of_keys <= max_num_of_child_nodes - 1) // parent node에 공간이 있는 경우
                return;

            else // parent node에 공간이 없는 경우
            {
                Node *new_internal_node = split_internal_node(parent_node);
                insert_to_parent_node(parent_node, new_internal_node, parent_node->keys[parent_node->num_of_keys]);
            }
        }
    }

    Node *split_internal_node(Node *node)
    {
        // 노드가 겹치지 않도록 파일 끝에 새로운 노드를 생성
        index_file.seekp(0, ios::end);
        long new_file_offset = index_file.tellp();

        Node *new_right_internal_node = new Node(max_num_of_child_nodes, new_file_offset, false);

        new_right_internal_node->right_node = node->right_node;
        int mid_idx = max_num_of_child_nodes / 2;
        node->right_node = node->left_children[mid_idx];

        node->num_of_keys = mid_idx;
        new_right_internal_node->num_of_keys = max_num_of_child_nodes - mid_idx - 1;

        for (int i = 0; i < new_right_internal_node->num_of_keys; i++)
        {
            new_right_internal_node->keys[i] = node->keys[i + mid_idx + 1];
            new_right_internal_node->left_children[i] = node->left_children[i + mid_idx + 1];

            // 새로운 자식 노드의 부모 노드를 새로운 internal 노드로 설정
            Node *child_node = read_node_from_index_file(new_right_internal_node->left_children[i]);
            child_node->parent_node = new_right_internal_node->file_offset;

            write_node_to_index_file(child_node);
        }

        // 마지막 자식 노드의 부모 노드를 새로운 internal 노드로 설정
        Node *last_child_node = read_node_from_index_file(new_right_internal_node->right_node);
        last_child_node->parent_node = new_right_internal_node->file_offset;

        write_node_to_index_file(last_child_node);

        write_node_to_index_file(node);
        write_node_to_index_file(new_right_internal_node);

        return new_right_internal_node;
    }

    Node *single_key_search(int key, bool print_mode)
    {
        Node *current_node = read_node_from_index_file(root_offset);

        if (current_node == nullptr) // tree가 비어있는 경우
        {
            if (print_mode)
                cout << "NOT FOUND" << '\n';
            return current_node; // empty tree
        }

        int idx;

        while (!current_node->is_leaf) // leaf node까지 탐색
        {
            if (print_mode)
                current_node->print_all_keys();

            idx = current_node->find_key_index(key);
            if (idx == current_node->num_of_keys)
                current_node = read_node_from_index_file(current_node->right_node);
            else
                current_node = read_node_from_index_file(current_node->left_children[idx]);
        }

        for (idx = 0; idx < current_node->num_of_keys; idx++)
        {
            if (current_node->keys[idx] == key)
            {
                if (print_mode)
                    cout << current_node->values[idx] << '\n';
                return current_node;
            }
        }

        if (print_mode)
            cout << "NOT FOUND" << '\n';

        return current_node;
    }

    void ranged_search(int start_key, int end_key)
    {
        Node *current_node = single_key_search(start_key, false);

        if (current_node == nullptr) // tree가 비어있는 경우
        {
            cout << "NOT FOUND" << '\n';
            return;
        }

        if (current_node->keys[0] > end_key)
        {
            cout << "NOT FOUND" << '\n';
            return;
        }

        while (true)
        {
            for (int i = 0; i < current_node->num_of_keys; i++)
            {
                if (current_node->keys[i] >= start_key && current_node->keys[i] <= end_key)
                    cout << current_node->keys[i] << ", " << current_node->values[i] << '\n';
                else if (current_node->keys[i] > end_key)
                    return;
            }
            if (current_node->right_node == 0)
                break;
            current_node = read_node_from_index_file(current_node->right_node);
        }
    }

    void delete_key(int key)
    {
        if (root_offset == 0) // [Case 1] tree가 비어있는 경우
        {
            cout << "<Error>" << '\n'
                 << "Tree is empty" << '\n';
            return;
        }

        Node *leaf_node = single_key_search(key, false);
        int idx;
        for (idx = 0; idx < leaf_node->num_of_keys; idx++) // key가 존재하는지 확인 : find_key_index 함수를 사용하지 않는 이유는, key의 위치 + 1을 반환하기 때문
            if (leaf_node->keys[idx] == key)
                break;

        if (idx == leaf_node->num_of_keys) // [Case 2] tree에 해당 key가 존재하지 않는 경우
        {
            cout << "<Error>" << '\n'
                 << "key not found : " << key << '\n';
            return;
        }

        // [Case 3] tree에 해당 key가 존재하는 경우

        leaf_node->keys.erase(leaf_node->keys.begin() + idx);
        leaf_node->values.erase(leaf_node->values.begin() + idx);
        leaf_node->num_of_keys--;

        if (leaf_node->num_of_keys >= min_num_of_keys) // 삭제 후 leaf node가 underflow가 발생하지 않는 경우 (최소 key 개수를 만족하는 경우)
            write_node_to_index_file(leaf_node);

        else // 삭제 후 leaf node가 underflow가 발생하는 경우 (최소 key 개수보다 작아지는 경우)
        {
            Node *sibling_node = find_sibling_node(leaf_node);

            if (sibling_node != nullptr) // key를 빌려올 수 있는 sibling node가 존재하는 경우
                borrow_key_from_sibling_node(leaf_node, sibling_node);
            else // key를 빌려올 수 있는 sibling node가 존재하지 않는 경우
                merge_nodes(leaf_node);
        }
    }

    Node *find_sibling_node(Node *node) // key를 빌려올 수 있는 sibling node가 존재하면 return, 존재하지 않으면 nullptr를 return
    {
        Node *parent_node = read_node_from_index_file(node->parent_node);

        if (parent_node->left_children[0] == node->file_offset) // 인자로 받은 node가 parent node의 첫번째 자식인 경우 : 오른쪽 sibling node만 가져올 수 있음
        {
            Node *right_sibling_node;
            if (parent_node->num_of_keys == 1) // parent node의 key가 1개인 경우
            {
                right_sibling_node = read_node_from_index_file(parent_node->right_node);

                if (right_sibling_node->num_of_keys > min_num_of_keys) // right sibling node가 key를 빌려줄 수 있는 경우
                    return right_sibling_node;
                else // right sibling node가 key를 빌려줄 수 없는 경우
                    return nullptr;
            }
            else // parent node의 key가 2개 이상인 경우
            {
                right_sibling_node = read_node_from_index_file(parent_node->left_children[1]);

                if (right_sibling_node->num_of_keys > min_num_of_keys) // right sibling node가 key를 빌려줄 수 있는 경우
                    return right_sibling_node;
                else // right sibling node가 key를 빌려줄 수 없는 경우
                    return nullptr;
            }
        }

        else if (parent_node->right_node == node->file_offset) // 인자로 받은 node가 parent node의 마지막 자식인 경우 : 왼쪽 sibling node만 가져올 수 있음
        {
            Node *left_sibling_node = read_node_from_index_file(parent_node->left_children[parent_node->num_of_keys - 1]);

            if (left_sibling_node->num_of_keys > min_num_of_keys) // left sibling node가 key를 빌려줄 수 있는 경우
                return left_sibling_node;
            else // left sibling node가 key를 빌려줄 수 없는 경우
                return nullptr;
        }

        else // 인자로 받은 node가 parent node의 중간 자식인 경우 : 양쪽 sibling node 모두 가져올 수 있음
        {
            int idx = 0; // parent_node에서 node의 index를 저장
            while (idx < parent_node->num_of_keys && parent_node->left_children[idx] != node->file_offset)
                idx++;

            Node *left_sibling_node = read_node_from_index_file(parent_node->left_children[idx - 1]);
            if (left_sibling_node->num_of_keys > min_num_of_keys) // left sibling node가 key를 빌려줄 수 있는 경우
                return left_sibling_node;
            else // left sibling node가 key를 빌려줄 수 없는 경우
            {
                if (idx == parent_node->num_of_keys - 1) // right sibling node가 맨 오른쪽에 있는 경우
                {
                    Node *right_sibling_node = read_node_from_index_file(parent_node->right_node);
                    if (right_sibling_node->num_of_keys > min_num_of_keys) // right sibling node가 key를 빌려줄 수 있는 경우
                        return right_sibling_node;
                    else // right sibling node가 key를 빌려줄 수 없는 경우
                        return nullptr;
                }
                else // right sibling node가 중간에 있는 경우
                {
                    Node *right_sibling_node = read_node_from_index_file(parent_node->left_children[idx + 1]);
                    if (right_sibling_node->num_of_keys > min_num_of_keys) // right sibling node가 key를 빌려줄 수 있는 경우
                        return right_sibling_node;
                    else // right sibling node가 key를 빌려줄 수 없는 경우
                        return nullptr;
                }
            }
        }
    }

    void borrow_key_from_sibling_node(Node *node, Node *sibling_node) // sibling node로부터 key를 빌려오는 함수
    {
        Node *parent_node = read_node_from_index_file(node->parent_node);

        int idx = 0; // parent node에서 node의 index를 저장
        while (idx < parent_node->num_of_keys && parent_node->left_children[idx] != node->file_offset)
            idx++;

        if (idx == parent_node->num_of_keys) // [Case 1] node가 parent node의 마지막 자식인 경우
        {
            // parent_node의 마지막 key를 sibling_node의 마지막 key로 바꿈
            parent_node->keys[parent_node->num_of_keys - 1] = sibling_node->keys[sibling_node->num_of_keys - 1];

            // node의 첫번째 key를 parent_node의 마지막 key로 바꿈
            node->keys.insert(node->keys.begin(), sibling_node->keys[sibling_node->num_of_keys - 1]);
            node->values.insert(node->values.begin(), sibling_node->values[sibling_node->num_of_keys - 1]);
            node->num_of_keys++;

            // sibling_node의 마지막 key 제거
            sibling_node->keys.pop_back();
            sibling_node->values.pop_back();
            sibling_node->num_of_keys--;

            write_node_to_index_file(parent_node);
            write_node_to_index_file(node);
            write_node_to_index_file(sibling_node);
        }
        else if (idx == 0) // [Case 2] node가 parent node의 첫번째 자식인 경우
        {
            // parent_node의 첫번째 key를 sibling_node의 두 번째 key로 바꿈 : [Case 1]과 다르게 sibling_node의 두 번째 key를 옮겨야함
            parent_node->keys[0] = sibling_node->keys[1];

            // sibling_node의 첫번째 key를 node의 마지막 key로 바꿈
            node->keys[node->num_of_keys] = sibling_node->keys[0];
            node->values[node->num_of_keys] = sibling_node->values[0];

            // keys와 values의 크기를 미리 초기화해줬기 때문에, push_back을 사용하면 node의 마지막이 아닌 vector의 마지막에 삽입되서 안됨
            // node->keys.push_back(sibling_node->keys[0]);
            // node->values.push_back(sibling_node->values[0]);
            node->num_of_keys++;

            // sibling_node의 첫번째 key 제거
            sibling_node->keys.erase(sibling_node->keys.begin());
            sibling_node->values.erase(sibling_node->values.begin());
            sibling_node->num_of_keys--;

            write_node_to_index_file(parent_node);
            write_node_to_index_file(node);
            write_node_to_index_file(sibling_node);
        }
        else // [Case 3] node가 parent node의 중간 자식인 경우
        {
            int sibling_idx = 0; // parent node에서 sibling node의 index를 저장
            while (sibling_idx < parent_node->num_of_keys && parent_node->left_children[sibling_idx] != sibling_node->file_offset)
                sibling_idx++;

            if (sibling_idx < idx) // sibling node가 node의 왼쪽에 있는 경우
            {
                // parent_node의 (idx-1) key를 sibling_node의 마지막 key로 바꿈
                parent_node->keys[idx - 1] = sibling_node->keys[sibling_node->num_of_keys - 1];

                // node의 첫번째 key를 parent_node의 sibling_node의 마지막 key로 바꿈
                node->keys.insert(node->keys.begin(), sibling_node->keys[sibling_node->num_of_keys - 1]);
                node->values.insert(node->values.begin(), sibling_node->values[sibling_node->num_of_keys - 1]);
                node->num_of_keys++;

                // sibling_node의 마지막 key 제거
                sibling_node->keys.pop_back();
                sibling_node->values.pop_back();
                sibling_node->num_of_keys--;

                write_node_to_index_file(parent_node);
                write_node_to_index_file(node);
                write_node_to_index_file(sibling_node);
            }
            else // sibling node가 node의 오른쪽에 있는 경우
            {
                if (sibling_idx == parent_node->num_of_keys) // sibling node가 parent node의 마지막 자식인 경우
                {
                    // parent_node의 idx key를 sibling_node의 두 번째 key로 바꿈
                    parent_node->keys[idx] = sibling_node->keys[1];

                    node->keys[node->num_of_keys] = sibling_node->keys[0];
                    node->values[node->num_of_keys] = sibling_node->values[0];

                    // keys와 values의 크기를 미리 초기화해줬기 때문에, push_back을 사용하면 node의 마지막이 아닌 vector의 마지막에 삽입되서 안됨
                    // node->keys.push_back(sibling_node->keys[0]);
                    // node->values.push_back(sibling_node->values[0]);
                    node->num_of_keys++;

                    sibling_node->keys.erase(sibling_node->keys.begin());
                    sibling_node->values.erase(sibling_node->values.begin());
                    sibling_node->num_of_keys--;

                    write_node_to_index_file(parent_node);
                    write_node_to_index_file(node);
                    write_node_to_index_file(sibling_node);
                }
                else // sibling node가 parent node의 중간 자식인 경우
                {
                    // parent_node의 idx key를 sibling_node의 두 번째 key로 바꿈
                    parent_node->keys[idx] = sibling_node->keys[1];

                    node->keys[node->num_of_keys] = sibling_node->keys[0];
                    node->values[node->num_of_keys] = sibling_node->values[0];

                    // keys와 values의 크기를 미리 초기화해줬기 때문에, push_back을 사용하면 node의 마지막이 아닌 vector의 마지막에 삽입되서 안됨
                    // node->keys.push_back(sibling_node->keys[0]);
                    // node->values.push_back(sibling_node->values[0]);
                    node->num_of_keys++;

                    sibling_node->keys.erase(sibling_node->keys.begin());
                    sibling_node->values.erase(sibling_node->values.begin());
                    sibling_node->num_of_keys--;

                    write_node_to_index_file(parent_node);
                    write_node_to_index_file(node);
                    write_node_to_index_file(sibling_node);
                }
            }
        }
    }

    void merge_nodes(Node *node)
    {
        write_node_to_index_file(node);
    }

    void traverse_tree(Node *current_node)
    {
        if (current_node == nullptr)
        {
            cout << "Tree is empty" << '\n';
            return;
        }

        int idx = 0;
        for (idx = 0; idx < current_node->num_of_keys; idx++)
        {
            if (current_node->is_leaf)
            {
                cout << "<leaf>" << '\n'
                     << " key: " << current_node->keys[idx] << ", value: " << current_node->values[idx] << '\n';
                cout << "해당 노드가 가리키는 부모 노드의 키 : ";
                read_node_from_index_file(current_node->parent_node)->print_all_keys();
                cout << '\n';
            }
            else if (current_node->parent_node == 0)
            {
                cout << "<root>" << '\n'
                     << " key: " << current_node->keys[idx] << '\n';
                cout << "해당 노드가 가리키는 부모 노드의 키 : ";
                read_node_from_index_file(current_node->parent_node)->print_all_keys();
                cout << '\n';
            }
            else
            {
                cout << "<internal>" << '\n'
                     << " key: " << current_node->keys[idx] << '\n';
                cout << "해당 노드가 가리키는 부모 노드의 키 : ";
                read_node_from_index_file(current_node->parent_node)->print_all_keys();
                cout << '\n';
            }

            if (current_node->left_children[idx] != 0)
                traverse_tree(read_node_from_index_file(current_node->left_children[idx]));
        }
        if (!current_node->is_leaf && current_node->right_node != 0)
        {
            cout << "right_node 시작" << '\n';
            traverse_tree(read_node_from_index_file(current_node->right_node));
            cout << "right_node 끝" << '\n';
        }
    }
};

int main(int argc, char *argv[])
{
    int key, value;
    int start_key, end_key;

    if (strcmp(argv[1], "-c") == 0)
    {
        long root_offset = 0; // index 파일에 저장할 root node의 offset (metadata) : 처음에는 empty tree이므로 0으로 초기화

        index_file_name = argv[2];
        int max_num_of_child_nodes = atoi(argv[3]);

        ofstream index_file(index_file_name, ios::binary);
        if (!index_file)
        {
            cout << "<Error>" << '\n'
                 << "create index file failed" << '\n';
            exit(1);
        }

        index_file.write(reinterpret_cast<char *>(&max_num_of_child_nodes), sizeof(int));
        index_file.write(reinterpret_cast<char *>(&root_offset), sizeof(long));
        index_file.flush();
    }
    else if (strcmp(argv[1], "-i") == 0)
    {
        index_file_name = argv[2];
        data_file_name = argv[3];

        ifstream data_file(data_file_name);
        if (!data_file)
        {
            cout << "<Error>" << '\n'
                 << "open data file failed" << '\n';
            return 1;
        }

        BPTree tree;

        string line;
        while (getline(data_file, line))
        {
            if (line.empty())
                continue; // 빈 줄 건너뛰기

            stringstream ss(line);
            string key_str, value_str;
            if (getline(ss, key_str, ',') && getline(ss, value_str, ','))
            {
                key = stoi(key_str);
                value = stoi(value_str);

                /* debug */
                // cout << '\n'
                //      << "<insert key> : " << key << ", <value> : " << value << '\n'
                //      << '\n';
            }

            tree.insert(key, value);
        }
    }
    else if (strcmp(argv[1], "-d") == 0)
    {
        index_file_name = argv[2];
        data_file_name = argv[3];

        ifstream data_file(data_file_name);
        if (!data_file)
        {
            cout << "<Error>" << '\n'
                 << "open data file failed" << '\n';
            return 1;
        }

        BPTree tree;

        while (data_file >> key)
        {
            /* debug */
            // cout << "delete key : " << key << '\n';

            tree.delete_key(key);
        }
    }
    else if (strcmp(argv[1], "-s") == 0)
    {
        index_file_name = argv[2];
        key = atoi(argv[3]);

        BPTree tree;

        /* debug */
        // cout << "search key : " << key << '\n';

        tree.single_key_search(key, true);
    }
    else if (strcmp(argv[1], "-r") == 0)
    {
        index_file_name = argv[2];
        start_key = atoi(argv[3]);
        end_key = atoi(argv[4]);

        /* debug */
        // cout << "start_key : " << start_key << ", end_key : " << end_key << '\n';

        BPTree tree;
        tree.ranged_search(start_key, end_key);
    }
    else if (strcmp(argv[1], "-tr") == 0) // 디버깅용 traverse 함수
    {
        index_file_name = argv[2];

        BPTree tree;
        tree.traverse_tree(tree.root);
    }
    else
    {
        cout << "<Option>" << '\n'
             << "-c : Creation" << '\n'
             << "-i : Insertion" << '\n'
             << "-d : Deletion" << '\n'
             << "-s : Single Key Search " << '\n'
             << "-r : Ranged Search" << '\n';
        return 1;
    }
    return 0;
}
