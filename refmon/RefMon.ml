#load "str.cma";;

module type RESOURCE_MGR = 
  sig 

		type operator 
		type filename = string

		type command = operator * filename

		type result 

		val execute :
			string ->		(* What directory is this resource manager running in (for ease of use so all servers can run off the same code) *)
			command -> result      (* May also raise an exception! *)

		val get_operator :
			string -> operator

		val get_operator_string :
			operator -> string
	end
;;

module type REFERENCE_MONITOR = 
	sig 

		type principal                       (* Who is requesting the command*)

		type operator 
		type filename = string

		type request = principal* operator * filename

		type result 

		val execute :
			principal ->		(* Who is this reference monitor running as (for ease of use so all servers can run off the same code) *)
			request -> result      (* May also raise an exception! *)
    
		val add_authorization : 
			principal ->		(* Who is this reference monitor running as (for ease of use so all servers can run off the same code) *)
			principal *                   (* Granting the authorization *)
			principal *                   (* to be allowed *)
			operator *                    (* what permitted *)
			filename -> bool            (* succeed/fail *)

		val delete_authorization : 
			principal ->		(* Who is this reference monitor running as (for ease of use so all servers can run off the same code) *)
			principal *                (* Withdrawing the authorization *)
			principal *                (* to be denied *)
			operator *                 (* what is prohibited *)
			filename -> bool           (* succeed/fail *)

        (* add and delete authorization should also 
           cover groups of principals, etc.        *)

		val add_group_member : 
			principal ->		(* Who is this reference monitor running as (for ease of use so all servers can run off the same code) *)
			principal *                     (* Granting the membership *)
			principal *                     (* the grantee *)
			principal                       (* the group, also treated as a principal *)
			-> bool                           (* succeed/fail *)

		val delete_group_member : 
			principal ->		(* Who is this reference monitor running as (for ease of use so all servers can run off the same code) *)
			principal *                     (* Removing the membership *)
			principal *                     (* the victim *)
			principal                       (* the group, also treated as a principal *)
			-> bool                           (* succeed/fail *)

		val get_principal :
			string -> principal

		val get_operator :
			string -> operator
	end
;;

let error message =
	print_endline message;
	raise Exit
;;

module RefMon : REFERENCE_MONITOR =
	struct
		module OpenSSL =
			struct
				let encrypt ((user : string), (in_file : string), (out_file : string)) =
					let username_lowercase = String.lowercase user in
					let key_file = "../CA/" ^ username_lowercase ^ "/" ^ username_lowercase ^ ".key" in
					ignore (Sys.command ("openssl enc -aes-256-cbc -a -kfile " ^ key_file ^ " -in " ^ in_file ^ " -out " ^ out_file))

				let decrypt ((user : string), (in_file : string), (out_file : string)) =
					let username_lowercase = String.lowercase user in
					let key_file = "../CA/" ^ username_lowercase ^ "/" ^ username_lowercase ^ ".key" in
					ignore (Sys.command ("openssl enc -d -aes-256-cbc -a -kfile " ^ key_file ^ " -in " ^ in_file ^ " -out " ^ out_file))

				let hash ((user : string), (str : string)) =
					let hashfile = "h.tmp" in
					let outfile = "out.tmp" in
					let f = open_out hashfile in
					Printf.fprintf f "%s" str;
					close_out f;
					let g = open_out outfile in
					close_out g;
					ignore (Sys.command ("openssl dgst -sha256 -hex -out " ^ outfile ^ " " ^ hashfile));
					let read_from = open_in outfile in
					let hashed_str = input_line read_from in
					close_in read_from;
					Sys.remove hashfile;
					Sys.remove outfile;
					let just_hash = String.sub hashed_str 15 ((String.length hashed_str) - 15) in
					just_hash
			end

		module ResMan : RESOURCE_MGR =
			struct
				type operator = 
					| GET
					| PUT
					| DEL
				type filename = string
				type result = string
				type command = operator * filename

				let file_directory = "../files/"

				let get_operator (op_name : string) =
					match op_name with
						| "get" -> GET
						| "put" -> PUT
						| "del" -> DEL
						| _ -> error "Bad operator"

				let get_operator_string (op : operator) =
					match op with
						| GET -> "get"
						| PUT -> "put"
						| DEL -> "del"

				let execute (host_name : string) (command : command) =
					let operator, file = command in
					let hashed_filename = OpenSSL.hash (host_name, file) in
					let encrypted_file = host_name ^ "/files/" ^ hashed_filename in
					let plaintext_file = file_directory ^ file in
					match operator with
						| GET ->
							if Sys.file_exists encrypted_file then
								(OpenSSL.decrypt (host_name, encrypted_file, plaintext_file);
								"Success")
							else
								"Failure"
						| PUT ->
							if Sys.file_exists encrypted_file then
								Sys.remove encrypted_file;
							let f = open_out encrypted_file in
							close_out f;
							OpenSSL.encrypt (host_name, plaintext_file, encrypted_file);
							"Success"
						| DEL ->
							if Sys.file_exists encrypted_file then
								Sys.remove encrypted_file;
							"Success"
			end

		type operator = ResMan.operator
		type filename = string
		type result = ResMan.result

		type principal =
			| PERSON of string
			| GROUP of string

		type request = principal* operator * filename

		module UserPermissions = Map.Make (String)
		module Groups = Map.Make (String)

		let dict = ref UserPermissions.empty
		let groups = ref Groups.empty
		let owners = ref []

		let get_operator (op_name : string) =
			ResMan.get_operator op_name
		
		(* It would be nice to parameterize these so we don't have to modify the source to add users or groups *)
		let get_principal (name : string) =
			match name with
				| "Jane" -> PERSON "Jane"
				| "Jack" -> PERSON "Jack"
				| "Joe" -> PERSON "Joe"
				| "Admin" -> GROUP "Admin"
				| "Group1" -> GROUP "Group1"
				| "Group2" -> GROUP "Group2"
				| _ -> error "Principal not in system"

		module Files =
			struct
				let user_permissions_file = "permissions.dat"
				let ownership_file = "ownership.dat"
				let groups_file = "groups.dat"

				let create file =
					let f = open_out file in
					close_out f

				let delete file =
					if Sys.file_exists file then
						Sys.remove file

				let format_values_for_writing (str : string) value =
					let (filename, operator) = value in
					let out = str ^ "(" ^ filename ^ "," ^ (ResMan.get_operator_string operator) ^ ") " in
					out

				let format_line_for_writing (user : string) (value : 'a list) (str : string) =
					let start = str ^ user ^ " [ " in
					let vals = List.fold_left format_values_for_writing start value in
					let out = vals ^ "]\n" in
					out

				let write_users_to_file (host_name : string) (file : filename) =
					delete file;
					let write_to = open_out file in
					let str = UserPermissions.fold format_line_for_writing !dict in
					Printf.fprintf write_to "%s" (str "");
					close_out write_to;
					let encrypted_file = host_name ^ "/" ^ file in
					delete encrypted_file;
					OpenSSL.encrypt (host_name, file, encrypted_file);
					delete file

				let parse_string_to_permissions line =
					let is_match_val (value : string) =
						((String.get value 0) = '(') in
					let make_list file_list (str : string) =
						let str = String.sub str 1 (String.length str - 2) in
						let filename_op = Str.split (Str.regexp ",") str in
						let filename = List.nth filename_op 0 in
						let operator = get_operator (List.nth filename_op 1) in
						let file_list = (filename, operator) :: file_list in
						file_list in
					let vals = Str.split (Str.regexp "[ ]+") line in
					let files = List.filter is_match_val vals in
					let file_permissions = List.fold_left make_list [] files in
					try
						dict := UserPermissions.add (List.nth vals 0) file_permissions (!dict)
					with e ->
						raise e

				let print_users () =
					print_endline (UserPermissions.fold format_line_for_writing !dict "")

				let format_owners_for_writing (str : string) value =
					let (filename, owner) = value in
					let out = str ^ "(" ^ filename ^ "," ^ owner ^ ") " in
					out

				let write_owners_to_file (host_name : string) (file : filename) =
					delete file;
					let write_to = open_out file in
					let str = List.fold_left format_owners_for_writing "" !owners in
					Printf.fprintf write_to "%s" str;
					close_out write_to;
					let encrypted_file = host_name ^ "/" ^ file in
					delete encrypted_file;
					OpenSSL.encrypt (host_name, file, encrypted_file);
					delete file

				let parse_string_to_owners_list line =
					let make_list file_list (str : string) =
						let str = String.sub str 1 (String.length str - 2) in
						let filename_owner = Str.split (Str.regexp ",") str in
						let owner = List.nth filename_owner 0 in
						let filename = List.nth filename_owner 1 in
						let file_list = (owner, filename) :: file_list in
						file_list in
					let vals = Str.split (Str.regexp "[ ]+") line in
					let file_owners = List.fold_left make_list [] vals in
					owners := file_owners

				let print_owners () =
					print_endline (List.fold_left format_owners_for_writing "" !owners)

				let format_group_members_for_writing (str : string) (member : string) =
					let out = str ^ member ^ " " in
					out

				let format_group_for_writing (group : string) (members : string list) (str : string) =
					let start = str ^ group ^ " " in
					let vals = List.fold_left format_group_members_for_writing start members in
					let out = vals ^ "\n" in
					out

				let write_groups_to_file (host_name : string) (file : filename) =
					delete file;
					let write_to = open_out file in
					let str = Groups.fold format_group_for_writing !groups in
					Printf.fprintf write_to "%s" (str "");
					close_out write_to;
					let encrypted_file = host_name ^ "/" ^ file in
					delete encrypted_file;
					OpenSSL.encrypt (host_name, file, encrypted_file);
					delete file

				let parse_string_to_groups (line : string) =
					let vals = Str.split (Str.regexp "[ ]+") line in
					let principals = List.tl vals in
					try
						groups := Groups.add (List.hd vals) principals (!groups)
					with e ->
						raise e

				let read_from_file (host_name : string) (file : filename) funct =
					let encrypted_file = host_name ^ "/" ^ file in
					if (Sys.file_exists encrypted_file) then
						(OpenSSL.decrypt (host_name, encrypted_file, file));
					if not (Sys.file_exists file) then
						create file;
					let lines = ref [] in
					let read_from = open_in file in
					try
						while true do
					    	lines := input_line read_from :: !lines
						done;
					with End_of_file ->
						close_in read_from;
					List.iter funct !lines;
					delete file

				let print_groups () =
					print_endline (Groups.fold format_group_for_writing !groups "")
			end

		module RefMonHelpers =
			struct
				let add_new_file_ownership (host_name : string) owner =
					let (principal_name, filename) = owner in
					owners := owner :: !owners;
					Files.write_owners_to_file host_name Files.ownership_file;

					Files.read_from_file host_name Files.user_permissions_file Files.parse_string_to_permissions;
					try
						let vals = UserPermissions.find principal_name (!dict) in
						let vals = (filename, get_operator "get") :: vals in
						let vals = (filename, get_operator "put") :: vals in
						let vals = (filename, get_operator "del") :: vals in
						dict := UserPermissions.add principal_name vals (!dict);
						Files.write_users_to_file host_name Files.user_permissions_file
					with Not_found ->
						let vals = [] in
						let vals = (filename, get_operator "get") :: vals in
						let vals = (filename, get_operator "put") :: vals in
						let vals = (filename, get_operator "del") :: vals in
						dict := UserPermissions.add principal_name vals (!dict);
						Files.write_users_to_file host_name Files.user_permissions_file

				let ensure_at_least_one_admin (host_name : string) =
					try
						let adminMembers = Groups.find "Admin" (!groups) in
						if List.length adminMembers = 0 then
							(print_endline ("There were no admins! " ^  host_name ^ " is now an admin");
							groups := (Groups.add "Admin" [host_name] (!groups));
							Files.write_groups_to_file host_name Files.groups_file)
					with Not_found ->
						print_endline ("There were no admins! " ^  host_name ^ " is now an admin");
						groups := (Groups.add "Admin" [host_name] (!groups));
						Files.write_groups_to_file host_name Files.groups_file

				let user_is_in_group ((group_name : string), (user_name : string)) =
					let user_found username =
						(username = user_name) in
					let users = Groups.find group_name !groups in
					(List.exists user_found users)

				let user_has_permission (host_name : string) ((principal_name : string), (operator: operator), (filename : filename)) =
					Files.read_from_file host_name Files.user_permissions_file Files.parse_string_to_permissions;
					let permissions_found item =
						let (file, op) = item in
						((file = filename) && (op = operator)) in

					let user_in_list (group_name : string) (members : string list) =
						let user_found username =
							(username = principal_name) in
						(List.exists user_found members) in

					let group_with_permission (group_name : string) (members : string list) =
						try
							let group_permissions = UserPermissions.find group_name (!dict) in
							(List.exists permissions_found group_permissions)
						with Not_found ->
							false in

					let does_group_have_permission (host_name : string) =
						(* Check if the user is part of a group with permission *)
						Files.read_from_file host_name Files.groups_file Files.parse_string_to_groups;
						let groups_belonging_to = Groups.filter user_in_list !groups in
						Groups.exists group_with_permission groups_belonging_to in

					try
						let user_permissions = UserPermissions.find principal_name (!dict) in
						if (List.exists permissions_found user_permissions) then
							true
						else
							does_group_have_permission host_name
					with Not_found ->
						does_group_have_permission host_name

				let user_owns_file (host_name : string) ((principal_name : string), (filename : filename)) =
					Files.read_from_file host_name Files.ownership_file Files.parse_string_to_owners_list;
					let filename_found item =
						let (user, file) = item in
						((file = filename) && (user = principal_name)) in
					(List.exists filename_found !owners)
			end

		let add_authorization (host_user : principal) ((granter : principal), (grantee : principal), (operator : operator), (filename : filename)) =
			let host_name =
				match host_user with
					| PERSON n -> n
					| GROUP n -> error "A principal may not run a server as a group"
				in

			let granter_name =
				match granter with
					| PERSON n -> n
					| GROUP n -> error "Groups may not perform actions"
				in

			if RefMonHelpers.user_owns_file host_name (granter_name, filename) then
				(let grantee_name =
					match grantee with
						| PERSON n -> n
						| GROUP n -> n
					in

				Files.read_from_file host_name Files.user_permissions_file Files.parse_string_to_permissions;

				try
					let vals = UserPermissions.find grantee_name (!dict) in
					let newVals = (filename, operator) :: vals in
					dict := UserPermissions.add grantee_name newVals (!dict);
					Files.write_users_to_file host_name Files.user_permissions_file;
					true
				with Not_found ->
					dict := UserPermissions.add grantee_name [(filename, operator)] (!dict);
					Files.write_users_to_file host_name Files.user_permissions_file;
					true)
			else
				false

		let delete_authorization (host_user : principal) ((granter : principal), (grantee : principal), (operator : operator), (filename : filename)) =
			let host_name =
				match host_user with
					| PERSON n -> n
					| GROUP n -> error "A principal may not run a server as a group"
				in

			let granter_name =
				match granter with
					| PERSON n -> n
					| GROUP n -> error "Groups may not perform actions"
				in

			if RefMonHelpers.user_owns_file host_name (granter_name, filename) then
				(let grantee_name =
					match grantee with
						| PERSON n -> n
						| GROUP n -> n
					in

				let is_match_value value =
					let (file_name, operator) = value in
					let file_name_match = (file_name <> filename) in
					let operator_match = (operator <> operator) in
					(file_name_match || operator_match) in

				Files.read_from_file host_name Files.user_permissions_file Files.parse_string_to_permissions;

				try
					let vals = UserPermissions.find grantee_name (!dict) in
					let newVals = List.filter is_match_value vals in
					dict := UserPermissions.add grantee_name newVals (!dict);

					Files.write_users_to_file host_name Files.user_permissions_file;
					true
				with Not_found ->
					true)
			else
				false

		let add_group_member (host_user : principal) ((granter : principal), (grantee : principal), (group : principal)) =
			let host_name =
				match host_user with
					| PERSON n -> n
					| GROUP n -> error "A principal may not run a server as a group"
				in

			let granter_name =
				match granter with
					| PERSON n -> n
					| GROUP n -> error "Groups may not perform actions"
				in

			Files.read_from_file host_name Files.groups_file Files.parse_string_to_groups;
			RefMonHelpers.ensure_at_least_one_admin host_name;

			if RefMonHelpers.user_is_in_group ("Admin", granter_name) then
				(let grantee_name =
					match grantee with
						| PERSON n -> n
						| GROUP n -> n
					in
				let group_name =
					match group with
						| PERSON n -> error (n ^ " is not a group")
						| GROUP n -> n
					in

				try
					let members = Groups.find group_name (!groups) in
					let newMembers = grantee_name :: members in
					groups := Groups.add group_name newMembers (!groups);
					Files.write_groups_to_file host_name Files.groups_file;
					true
				with Not_found ->
					groups := Groups.add group_name [grantee_name] (!groups);
					Files.write_groups_to_file host_name Files.groups_file;
					true)
			else
				false

		let delete_group_member (host_user : principal) ((granter : principal), (grantee : principal), (group : principal)) =
			let host_name =
				match host_user with
					| PERSON n -> n
					| GROUP n -> error "A principal may not run a server as a group"
				in

			let granter_name =
				match granter with
					| PERSON n -> n
					| GROUP n -> error "Groups may not perform actions"
				in
			
			Files.read_from_file host_name Files.groups_file Files.parse_string_to_groups;
			RefMonHelpers.ensure_at_least_one_admin host_name;

			if RefMonHelpers.user_is_in_group ("Admin", granter_name) then
				(let grantee_name =
					match grantee with
						| PERSON n -> n
						| GROUP n -> n
					in
				let group_name =
					match group with
						| PERSON n -> error (n ^ " is not a group")
						| GROUP n -> n
					in

				let is_match_value name =
					(name <> grantee_name) in

				try
					let members = Groups.find group_name (!groups) in
					let newMembers = List.filter is_match_value members in
					groups := Groups.add group_name newMembers (!groups);
					Files.write_groups_to_file host_name Files.groups_file;
					true
				with Not_found ->
					true)
			else
				false

		let execute (host_user : principal) (request : request) =
			let host_name =
				match host_user with
					| PERSON n -> n
					| GROUP n -> error "A principal may not run a server as a group"
				in

			let (principal, operator, filename) = request in
			let principal_name =
				match principal with
					| PERSON n -> n
					| GROUP n -> error "Groups may not perform actions"
				in

			Files.read_from_file host_name Files.ownership_file Files.parse_string_to_owners_list;

			let filename_found item =
				let (user, file) = item in
				(file = filename) in

			if (List.exists filename_found !owners) then
				(if RefMonHelpers.user_has_permission host_name (principal_name, operator, filename) then
					ResMan.execute host_name (operator, filename) (* THIS IS THE RETURN STATEMENT. Obvious, right? *)
				else
					error "Permission denied")
			else
				(if (operator = (get_operator "put")) then
					(RefMonHelpers.add_new_file_ownership host_name (principal_name, filename);
					ResMan.execute host_name (operator, filename)) (* This is also a return statement *)
				else
					error "File does not exist")
	end
;;


(*Scripts for interpreting a commandline input as OCaml types *)

let usage (t : string) =
	match t with
		| "execute" ->
			Printf.printf "Usage: %s [host_name] %s [user] [operator] [filename]\n" Sys.argv.(0) t;
			raise Exit
		| "add_authorization" ->
			Printf.printf "Usage: %s [host_name] %s [granter] [grantee] [operator] [filename]\n" Sys.argv.(0) t;
			raise Exit
		| "delete_authorization" ->
			Printf.printf "Usage: %s [host_name] %s [granter] [grantee] [operator] [filename]\n" Sys.argv.(0) t;
			raise Exit
		| "add_group_member" ->
			Printf.printf "Usage: %s [host_name] %s [granter] [grantee] [group]\n" Sys.argv.(0) t;
			raise Exit
		| "delete_group_member" ->
			Printf.printf "Usage: %s [host_name] %s [granter] [grantee] [group]\n" Sys.argv.(0) t;
			raise Exit
		| _ ->
			Printf.printf "Usage: %s [host_name] [command] ...\nValid commands are: execute, add_authorization, delete_authorization, add_group_member, and delete_group_member\n" Sys.argv.(0);
			raise Exit
;;

let parse_execute host_name =
	let host_user = RefMon.get_principal host_name in
	if Array.length Sys.argv < 5 then
		usage Sys.argv.(2);

	let principal = RefMon.get_principal Sys.argv.(3) in
	let operator = RefMon.get_operator Sys.argv.(4) in
	let filename = Sys.argv.(5) in

	ignore (RefMon.execute host_user (principal, operator, filename))
;;

let parse_add_authorization host_name =
	let host_user = RefMon.get_principal host_name in
	if Array.length Sys.argv < 7 then
		usage Sys.argv.(2);

	let granter = RefMon.get_principal Sys.argv.(3) in
	let grantee = RefMon.get_principal Sys.argv.(4) in
	let operator = RefMon.get_operator Sys.argv.(5) in
	let filename = Sys.argv.(6) in
	if RefMon.add_authorization host_user (granter, grantee, operator, filename) then
		print_endline "Success"
	else
		print_endline "You may only change permissions on your own files"
;;

let parse_delete_authorization host_name =
	let host_user = RefMon.get_principal host_name in
	if Array.length Sys.argv < 7 then
		usage Sys.argv.(2);

	let granter = RefMon.get_principal Sys.argv.(3) in
	let grantee = RefMon.get_principal Sys.argv.(4) in
	let operator = RefMon.get_operator Sys.argv.(5) in
	let filename = Sys.argv.(6) in
	if RefMon.delete_authorization host_user (granter, grantee, operator, filename) then
		print_endline "Success"
	else
		print_endline "You may only change permissions on your own files"
;;

let parse_add_group_member host_name =
	let host_user = RefMon.get_principal host_name in
	if Array.length Sys.argv < 6 then
		usage Sys.argv.(2);

	let granter = RefMon.get_principal Sys.argv.(3) in
	let grantee = RefMon.get_principal Sys.argv.(4) in
	let group = RefMon.get_principal Sys.argv.(5) in
	if RefMon.add_group_member host_user (granter, grantee, group) then
		print_endline "Success"
	else
		print_endline "You must be admin to modify groups"
;;

let parse_delete_group_member host_name =
	let host_user = RefMon.get_principal host_name in
	if Array.length Sys.argv < 6 then
		usage Sys.argv.(2);

	let granter = RefMon.get_principal Sys.argv.(3) in
	let grantee = RefMon.get_principal Sys.argv.(4) in
	let group = RefMon.get_principal Sys.argv.(5) in
	if RefMon.delete_group_member host_user (granter, grantee, group) then
		print_endline "Success"
	else
		print_endline "You must be admin to modify groups"
;;

(* Handle  parsing the input *)

if Array.length Sys.argv < 3 then
	usage ""
;;

let host_name = Sys.argv.(1);;

match Sys.argv.(2) with
	| "execute" -> parse_execute host_name
	| "add_authorization" -> parse_add_authorization host_name
	| "delete_authorization" -> parse_delete_authorization host_name
	| "add_group_member" -> parse_add_group_member host_name
	| "delete_group_member" -> parse_delete_group_member host_name
	| _ -> usage Sys.argv.(2);
;;
